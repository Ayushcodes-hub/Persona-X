from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, utc_now


class ResearchEvent(Base):
    """
    Persistent research job telemetry events for durable replay (Last-Event-ID)
    and cross-instance Server-Sent Events (SSE).
    """
    __tablename__ = "research_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)

    job = relationship("ResearchJob", backref="events")

    __table_args__ = (
        Index("ix_research_events_job_id_id", "job_id", "id"),
    )
