from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base, utc_now


class ResearchSnapshot(Base):
    __tablename__ = 'research_snapshots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    research_query_id: Mapped[int] = mapped_column(ForeignKey('research_queries.id'), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    retrieval_method: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_response: Mapped[str] = mapped_column(Text, nullable=False)
    response_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='captured', nullable=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
