from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    canonical_name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    aliases: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    primary_profession: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    professions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    nationality: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    birth_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    active_from: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    active_to: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    biography_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    identity_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    identity_status: Mapped[str] = mapped_column(String(50), default="unverified", nullable=False)

    ambiguity_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
