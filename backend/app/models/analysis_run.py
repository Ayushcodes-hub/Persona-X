from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id"), nullable=False, index=True
    )

    research_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("research_jobs.id"), nullable=True, index=True
    )

    analysis_type: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), default="started", nullable=False, index=True
    )

    input_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
