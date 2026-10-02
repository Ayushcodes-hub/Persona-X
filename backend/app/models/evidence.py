from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"), nullable=False, index=True
    )

    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="unverified", nullable=False
    )

    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_claim: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_locator: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    extraction_method: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    extraction_model: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
