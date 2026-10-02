import time
from typing import Any, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.core.config import get_settings

settings = get_settings()

if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )
else:
    # PostgreSQL / Supabase connection pooling configuration
    engine = create_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> Dict[str, Any]:
    """
    Perform a live database ping and measure query latency.
    """
    start_time = time.monotonic()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.monotonic() - start_time) * 1000, 2)
        return {
            "status": "connected",
            "dialect": engine.dialect.name,
            "latency_ms": latency_ms,
            "pool_size": getattr(engine.pool, "size", lambda: None)(),
            "is_supabase": settings.is_supabase_configured,
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "dialect": engine.dialect.name,
            "latency_ms": None,
            "is_supabase": settings.is_supabase_configured,
        }