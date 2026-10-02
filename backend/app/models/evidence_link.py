from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class EvidenceLink(Base):
    __tablename__ = "evidence_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )

    linked_evidence_id: Mapped[int] = mapped_column(
        ForeignKey("evidence.id"), nullable=False, index=True
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )

    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    confidence: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
