from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class SourceCapture(Base):
    __tablename__ = "source_captures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"), nullable=False, index=True
    )

    capture_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False, index=True
    )

    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    content_hash: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, index=True
    )

    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_content_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    capture_status: Mapped[str] = mapped_column(
        String(50), default="captured", nullable=False, index=True
    )

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
