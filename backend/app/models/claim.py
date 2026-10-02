from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )

    evidence_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("evidence.id"), nullable=True, index=True
    )

    statement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("statements.id"), nullable=True, index=True
    )

    claim_type: Mapped[str] = mapped_column(String(100), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    predicate: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    object_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    verification_status: Mapped[str] = mapped_column(
        String(50), default="unverified", nullable=False
    )

    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    analyst_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
