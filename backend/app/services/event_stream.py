import asyncio
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventStreamHub:
    """
    Durable and broadcast event hub for Server-Sent Events (SSE).
    Persists events to `research_events` table for reconnection replay (Last-Event-ID)
    and distributes real-time telemetry to subscribed browser clients.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._subscribers: Dict[int, List[asyncio.Queue]] = {}

    def publish(self, job_id: int, event_type: str, data: Dict[str, Any], stage: str = "orchestration") -> None:
        """
        Publish an event to all active SSE queues and persist to the database.
        """
        timestamp_str = datetime.now(timezone.utc).isoformat()
        event_id = None

        # Persist event to research_events table
        try:
            from backend.app.core.database import SessionLocal
            from backend.app.models.research_event import ResearchEvent

            db = SessionLocal()
            try:
                event_record = ResearchEvent(
                    job_id=job_id,
                    stage=stage or data.get("stage", "orchestration"),
                    event_type=event_type,
                    payload=data,
                )
                db.add(event_record)
                db.commit()
                db.refresh(event_record)
                event_id = event_record.id
            finally:
                db.close()
        except Exception as exc:
            logger.debug("Non-fatal: could not persist research event to DB: %s", exc)

        payload = {
            "id": event_id,
            "job_id": job_id,
            "event": event_type,
            "stage": stage,
            "data": data,
            "timestamp": timestamp_str,
        }

        with self._lock:
            subscribers = list(self._subscribers.get(job_id, []))

        for loop, q in subscribers:
            try:
                if loop.is_running():
                    loop.call_soon_threadsafe(q.put_nowait, payload)
                else:
                    q.put_nowait(payload)
            except Exception as exc:
                logger.debug("Failed to deliver SSE event: %s", exc)

    async def stream(self, job_id: int, last_event_id: Optional[int] = None) -> AsyncGenerator[str, None]:
        """
        Stream SSE events for a job, replaying missed events if last_event_id is provided.
        """
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        entry = (loop, queue)

        with self._lock:
            if job_id not in self._subscribers:
                self._subscribers[job_id] = []
            self._subscribers[job_id].append(entry)

        try:
            # 1. Yield initial connected event
            initial = {
                "job_id": job_id,
                "event": "connected",
                "data": {"status": "subscribed", "replaying": bool(last_event_id)},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            yield f"event: connected\ndata: {json.dumps(initial)}\n\n"

            # 2. Replay missed events from database if requested
            if last_event_id is not None:
                try:
                    from backend.app.core.database import SessionLocal
                    from backend.app.models.research_event import ResearchEvent

                    db = SessionLocal()
                    try:
                        past_events = (
                            db.query(ResearchEvent)
                            .filter(ResearchEvent.job_id == job_id, ResearchEvent.id > last_event_id)
                            .order_by(ResearchEvent.id.asc())
                            .all()
                        )
                        for ev in past_events:
                            replay_payload = {
                                "id": ev.id,
                                "job_id": ev.job_id,
                                "event": ev.event_type,
                                "stage": ev.stage,
                                "data": ev.payload,
                                "timestamp": ev.created_at.isoformat() if ev.created_at else None,
                            }
                            yield f"id: {ev.id}\nevent: {ev.event_type}\ndata: {json.dumps(replay_payload)}\n\n"
                    finally:
                        db.close()
                except Exception as exc:
                    logger.debug("Error replaying past events: %s", exc)

            # 3. Stream live events with 15s keep-alive heartbeats
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    event_name = payload.get("event", "message")
                    eid = payload.get("id")
                    id_prefix = f"id: {eid}\n" if eid else ""
                    yield f"{id_prefix}event: {event_name}\ndata: {json.dumps(payload)}\n\n"

                    if event_name in {"job_completed", "job_failed"}:
                        break
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            with self._lock:
                if job_id in self._subscribers and entry in self._subscribers[job_id]:
                    self._subscribers[job_id].remove(entry)
                    if not self._subscribers[job_id]:
                        del self._subscribers[job_id]

    async def subscribe(self, job_id: int) -> AsyncGenerator[str, None]:
        """Backward-compatible alias for stream()."""
        async for chunk in self.stream(job_id):
            yield chunk


event_hub = EventStreamHub()
