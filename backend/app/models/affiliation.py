from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Affiliation(Base):
    __tablename__ = "affiliations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )

    relationship_type: Mapped[str] = mapped_column(
        String(150), nullable=False, index=True
    )

    role_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    evidence_confidence: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    verification_status: Mapped[str] = mapped_column(
        String(50), default="unverified", nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
