from __future__ import annotations

import threading
import time
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.database import SessionLocal
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.services.event_stream import event_hub
from engine.identity.discovery import identity_discovery

from engine.research.orchestration.runtime import (
    ResearchOrchestrationRuntime,
)


class ResearchRateLimiter:
    """
    Thread-safe rolling-window rate limiter.

    This limits research-job starts rather than individual HTTP requests.
    The underlying Groq/browser calls remain controlled by the research
    execution service.
    """

    def __init__(self, requests_per_minute: int):
        if requests_per_minute < 1:
            raise ValueError(
                "requests_per_minute must be at least 1."
            )

        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0

        self._timestamps: deque[float] = deque()
        self._condition = threading.Condition()

    def acquire(self) -> None:
        while True:
            with self._condition:
                now = time.monotonic()

                while self._timestamps:
                    age = now - self._timestamps[0]

                    if age >= self.window_seconds:
                        self._timestamps.popleft()
                    else:
                        break

                if len(self._timestamps) < self.requests_per_minute:
                    self._timestamps.append(now)
                    return

                wait_seconds = (
                    self.window_seconds
                    - (now - self._timestamps[0])
                    + 0.01
                )

            time.sleep(max(wait_seconds, 0.01))


class ResearchJobManager:
    """
    Stage 50 persistent background research manager.

    Features:
    - bounded concurrency
    - independent SQLAlchemy session per worker
    - retries
    - exponential backoff
    - rate limiting
    - duplicate-job protection
    - stale-job recovery
    - persistent job state
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        max_attempts: Optional[int] = None,
        retry_base_seconds: Optional[float] = None,
        rate_limit_per_minute: Optional[int] = None,
        stale_job_seconds: Optional[int] = None,
    ):
        settings = get_settings()

        self.max_workers = (
            max_workers
            if max_workers is not None
            else settings.research_worker_count
        )

        self.max_attempts = (
            max_attempts
            if max_attempts is not None
            else settings.research_max_attempts
        )

        self.retry_base_seconds = (
            retry_base_seconds
            if retry_base_seconds is not None
            else settings.research_retry_base_seconds
        )

        self.stale_job_seconds = (
            stale_job_seconds
            if stale_job_seconds is not None
            else settings.research_stale_job_seconds
        )

        self.rate_limiter = ResearchRateLimiter(
            rate_limit_per_minute
            if rate_limit_per_minute is not None
            else settings.research_rate_limit_per_minute
        )

        self.executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="persona-research",
        )

        self._lock = threading.RLock()
        self._futures: Dict[int, Future] = {}
        self._started = False
        self._shutdown = False

    def start(self) -> None:
        with self._lock:
            if self._started and not self._shutdown:
                return

            if self._shutdown:
                self.executor = ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix="persona-x-research",
                )
                self._futures = {}
                self._shutdown = False

            self._started = True

    def shutdown(self, wait: bool = True) -> None:
        with self._lock:
            if self._shutdown:
                return

            self._shutdown = True

        self.executor.shutdown(
            wait=wait,
            cancel_futures=False,
        )

    def enqueue(
        self,
        job_id: int,
        force: bool = False,
    ) -> bool:
        """
        Queue a research job.

        Returns:
            True  -> a worker was submitted
            False -> job was already active/completed or unavailable
        """
        if job_id is None:
            raise ValueError("job_id is required.")

        with self._lock:
            if self._shutdown:
                raise RuntimeError(
                    "ResearchJobManager is shut down."
                )

            db = SessionLocal()

            try:
                job = (
                    db.query(ResearchJob)
                    .filter(ResearchJob.id == job_id)
                    .first()
                )

                if job is None:
                    return False

                if job.status in {"queued", "running"}:
                    if job_id in self._futures:
                        return False

                    if not force:
                        return False

                if job.status == "completed" and not force:
                    return False

                if job.status == "failed" and not force:
                    job.status = "queued"
                    job.error_message = None
                    job.current_stage = "queued"

                job.status = "queued"
                job.current_stage = "queued"
                job.error_message = None

                db.commit()

                future = self.executor.submit(
                    self._run_job,
                    job_id,
                )

                self._futures[job_id] = future

                future.add_done_callback(
                    lambda completed_future, jid=job_id: (
                        self._future_finished(
                            jid,
                            completed_future,
                        )
                    )
                )

                return True

            finally:
                db.close()

    def _future_finished(
        self,
        job_id: int,
        future: Future,
    ) -> None:
        with self._lock:
            self._futures.pop(job_id, None)

    @staticmethod
    def _get_attempt(
        job: ResearchJob,
    ) -> int:
        scope = job.requested_scope

        if not isinstance(scope, dict):
            return 0

        try:
            return int(
                scope.get(
                    "_stage50_attempt",
                    0,
                )
            )
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _set_attempt(
        job: ResearchJob,
        attempt: int,
    ) -> None:
        scope = job.requested_scope

        if not isinstance(scope, dict):
            scope = {}

        updated_scope = dict(scope)
        updated_scope["_stage50_attempt"] = attempt

        job.requested_scope = updated_scope

    def _run_job(
        self,
        job_id: int,
    ) -> None:
        db = SessionLocal()

        try:
            job = (
                db.query(ResearchJob)
                .filter(ResearchJob.id == job_id)
                .first()
            )

            if job is None:
                return

            current_attempt = self._get_attempt(job)

            if current_attempt >= self.max_attempts:
                job.status = "failed"
                job.current_stage = "failed"
                job.error_message = (
                    "Maximum Stage 50 research attempts exceeded."
                )
                db.commit()
                return

            attempt = current_attempt + 1

            self._set_attempt(
                job,
                attempt,
            )

            job.status = "running"
            job.current_stage = "queued"
            job.error_message = None

            db.commit()

        finally:
            db.close()

        try:
            self.rate_limiter.acquire()

            db = SessionLocal()

            try:
                job = (
                    db.query(ResearchJob)
                    .filter(ResearchJob.id == job_id)
                    .first()
                )

                if job is None:
                    return

                settings = get_settings()

                person = (
                    db.query(Person)
                    .filter(Person.id == job.person_id)
                    .first()
                )
                person_name = person.canonical_name if person else "Unknown"

                event_hub.publish(job_id, "job_started", {
                    "status": "running",
                    "stage": "identity",
                    "person_name": person_name,
                })

                candidates = []
                try:
                    candidates = identity_discovery.discover_candidates(person_name)
                except Exception:
                    candidates = []

                runtime = ResearchOrchestrationRuntime(
                    db=db,
                    identity_candidates=candidates,
                    max_queries=(
                        settings.research_max_queries_per_job
                    ),
                )

                result = runtime.run(
                    research_job_id=job_id,
                )

                refreshed_job = (
                    db.query(ResearchJob)
                    .filter(ResearchJob.id == job_id)
                    .first()
                )

                if refreshed_job is None:
                    return

                if result.status == "completed":
                    refreshed_job.status = "completed"
                    refreshed_job.current_stage = "dossier"
                    refreshed_job.error_message = None

                    self._set_attempt(
                        refreshed_job,
                        0,
                    )

                    db.commit()

                    event_hub.publish(job_id, "job_completed", {
                        "status": "completed",
                        "stage": "dossier",
                        "source_count": refreshed_job.source_count,
                        "evidence_count": refreshed_job.evidence_count,
                    })
                    return

                refreshed_job.status = "failed"
                refreshed_job.current_stage = (
                    result.current_stage or "failed"
                )
                refreshed_job.error_message = (
                    result.error
                    or "Research pipeline failed."
                )

                db.commit()

                event_hub.publish(job_id, "job_failed", {
                    "status": "failed",
                    "stage": refreshed_job.current_stage,
                    "error": refreshed_job.error_message,
                })

            finally:
                db.close()

        except Exception as exc:
            self._handle_failure(
                job_id=job_id,
                error=exc,
            )

    def _handle_failure(
        self,
        job_id: int,
        error: Exception,
    ) -> None:
        db = SessionLocal()

        try:
            job = (
                db.query(ResearchJob)
                .filter(ResearchJob.id == job_id)
                .first()
            )

            if job is None:
                return

            attempt = self._get_attempt(job)

            if attempt < self.max_attempts:
                delay = self.retry_base_seconds * (
                    2 ** max(attempt - 1, 0)
                )

                job.status = "queued"
                job.current_stage = "retry_wait"
                job.error_message = (
                    f"Stage 50 attempt {attempt} failed: "
                    f"{type(error).__name__}: {error}. "
                    f"Retrying in {delay:.2f} seconds."
                )

                db.commit()

                time.sleep(delay)

                with self._lock:
                    if self._shutdown:
                        return

                    future = self.executor.submit(
                        self._run_job,
                        job_id,
                    )

                    self._futures[job_id] = future

                    future.add_done_callback(
                        lambda completed_future, jid=job_id: (
                            self._future_finished(
                                jid,
                                completed_future,
                            )
                        )
                    )

                return

            job.status = "failed"
            job.current_stage = "failed"
            job.error_message = (
                f"Stage 50 exhausted "
                f"{self.max_attempts} attempt(s): "
                f"{type(error).__name__}: {error}"
            )

            db.commit()

        finally:
            db.close()

    def recover_stale_jobs(self) -> list[int]:
        """
        Recover jobs left in 'running' state after a process crash.

        A job is stale when updated_at is older than the configured
        recovery window.
        """
        db = SessionLocal()
        recovered: list[int] = []

        try:
            cutoff = datetime.now(timezone.utc) - timedelta(
                seconds=self.stale_job_seconds
            )

            stale_jobs = (
                db.query(ResearchJob)
                .filter(
                    ResearchJob.status == "running",
                    ResearchJob.updated_at < cutoff,
                )
                .all()
            )

            for job in stale_jobs:
                job.status = "queued"
                job.current_stage = "recovered"
                job.error_message = (
                    "Recovered by Stage 50 after "
                    "stale worker state."
                )

                recovered.append(job.id)

            db.commit()

        finally:
            db.close()

        for job_id in recovered:
            try:
                self.enqueue(
                    job_id=job_id,
                    force=True,
                )
            except Exception:
                continue

        return recovered

    def active_job_ids(self) -> list[int]:
        with self._lock:
            return list(
                self._futures.keys()
            )

    def active_count(self) -> int:
        with self._lock:
            return len(self._futures)

    def is_running(self) -> bool:
        with self._lock:
            return self._started and not self._shutdown

    def active_worker_count(self) -> int:
        return self.active_count()


research_job_manager = ResearchJobManager()
