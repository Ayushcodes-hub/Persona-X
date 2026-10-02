from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base, utc_now


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

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

    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    organization: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="documented",
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
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