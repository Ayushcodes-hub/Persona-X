from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, utc_now


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    canonical_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    aliases: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    organization_type: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    country: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    founded_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    dissolved_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_confidence: Mapped[float] = mapped_column(nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
