from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Statement(Base):
    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"), nullable=False, index=True
    )
    evidence_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("evidence.id"), nullable=True, index=True
    )

    statement_type: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    paraphrase: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    topic: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    statement_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    attribution_status: Mapped[str] = mapped_column(
        String(50), default="attributed", nullable=False
    )

    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
