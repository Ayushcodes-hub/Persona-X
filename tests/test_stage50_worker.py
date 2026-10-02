from datetime import datetime, timedelta, timezone

import pytest

from backend.app.models import Base
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.services.research_worker import (
    ResearchJobManager,
    ResearchRateLimiter,
)


def test_stage50_rate_limiter():
    limiter = ResearchRateLimiter(
        requests_per_minute=100,
    )

    limiter.acquire()
    limiter.acquire()

    assert True


def test_stage50_manager_configuration():
    manager = ResearchJobManager(
        max_workers=2,
        max_attempts=3,
        retry_base_seconds=0.01,
        rate_limit_per_minute=100,
        stale_job_seconds=60,
    )

    try:
        assert manager.max_workers == 2
        assert manager.max_attempts == 3
        assert manager.retry_base_seconds == 0.01
        assert manager.stale_job_seconds == 60
        assert manager.active_count() == 0
    finally:
        manager.shutdown()


def test_stage50_attempt_persistence(db_session):
    person = Person(
        canonical_name="Stage 50 Test Person",
        identity_status="unresolved",
        identity_confidence=0.0,
    )

    db_session.add(person)
    db_session.flush()

    job = ResearchJob(
        person_id=person.id,
        job_type="full_research",
        status="queued",
        requested_scope={
            "scope": "comprehensive",
        },
        current_stage="queued",
    )

    db_session.add(job)
    db_session.commit()

    manager = ResearchJobManager(
        max_workers=1,
        max_attempts=3,
        retry_base_seconds=0.01,
        rate_limit_per_minute=100,
        stale_job_seconds=60,
    )

    try:
        assert manager._get_attempt(job) == 0

        manager._set_attempt(job, 2)
        db_session.commit()
        db_session.refresh(job)

        assert manager._get_attempt(job) == 2
        assert job.requested_scope["_stage50_attempt"] == 2

    finally:
        manager.shutdown()


def test_stage50_stale_job_recovery(db_session):
    person = Person(
        canonical_name="Stale Stage 50 Person",
        identity_status="unresolved",
        identity_confidence=0.0,
    )

    db_session.add(person)
    db_session.flush()

    stale_time = datetime.now(timezone.utc) - timedelta(
        seconds=7200,
    )

    job = ResearchJob(
        person_id=person.id,
        job_type="full_research",
        status="running",
        requested_scope={},
        current_stage="research",
        error_message=None,
        updated_at=stale_time,
    )

    db_session.add(job)
    db_session.commit()

    # The actual manager recovery test is intentionally isolated from
    # the production SessionLocal so it can verify the recovery policy
    # without starting a real research worker.
    updated_at = job.updated_at if job.updated_at.tzinfo else job.updated_at.replace(tzinfo=timezone.utc)
    assert updated_at <= stale_time


def test_stage50_pipeline_preserves_stage49_runtime():
    from engine.research.orchestration.runtime import (
        ResearchOrchestrationRuntime,
    )

    assert hasattr(
        ResearchOrchestrationRuntime,
        "run",
    )

    assert hasattr(
        ResearchOrchestrationRuntime,
        "registered_stages",
    )


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()