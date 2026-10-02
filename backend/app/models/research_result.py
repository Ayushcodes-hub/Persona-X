from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class ResearchResult(Base):
    __tablename__ = "research_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    research_query_id: Mapped[int] = mapped_column(
        ForeignKey("research_queries.id"), nullable=False, index=True
    )

    source_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sources.id"), nullable=True, index=True
    )

    result_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    relevance_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    discovery_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), default="discovered", nullable=False, index=True
    )

    discovered_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
