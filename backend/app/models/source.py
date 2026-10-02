from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_tier: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    author: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )

    content_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)

    reliability_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
