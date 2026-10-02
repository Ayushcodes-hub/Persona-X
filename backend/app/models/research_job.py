from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base, utc_now


class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"),
        nullable=False,
        index=True,
    )

    job_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="queued",
        nullable=False,
        index=True,
    )

    requested_scope: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    query_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    source_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    evidence_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    current_stage: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )