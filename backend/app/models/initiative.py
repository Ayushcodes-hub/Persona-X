from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base, utc_now


class Initiative(Base):
    __tablename__ = "initiatives"

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

    name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    initiative_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    objective: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    lifecycle_stage: Mapped[str] = mapped_column(
        String(50),
        default="proposed",
        nullable=False,
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

    outcome: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    evaluation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
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