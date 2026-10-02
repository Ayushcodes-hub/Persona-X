from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class ResearchQuery(Base):
    __tablename__ = "research_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    research_job_id: Mapped[int] = mapped_column(
        ForeignKey("research_jobs.id"), nullable=False, index=True
    )

    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    profession_context: Mapped[Optional[str]] = mapped_column(
        String(150), nullable=True
    )
    topic: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False, index=True
    )

    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
