from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Dossier(Base):
    __tablename__ = "dossiers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )

    research_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("research_jobs.id"), nullable=True, index=True
    )

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="draft", nullable=False, index=True
    )

    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dossier_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completeness_score: Mapped[float] = mapped_column(default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
