import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.ai.accounting import ai_accounting
from backend.app.core.ai.router import ai_router
from backend.app.core.config import get_settings
from backend.app.core.database import get_db, check_db_health
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.models.source import Source
from backend.app.models.evidence import Evidence
from backend.app.models.dossier import Dossier
from backend.app.services.research_worker import research_job_manager

router = APIRouter(
    prefix="/system",
    tags=["system"],
)

_START_TIME = time.time()


@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    settings = get_settings()
    db_healthy = check_db_health()
    uptime_seconds = int(time.time() - _START_TIME)

    active_provider = settings.default_ai_provider
    provider_statuses = ai_router.test_all_connections()

    return {
        "status": "operational" if db_healthy else "degraded",
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "uptime_seconds": uptime_seconds,
        "database": {
            "status": "connected" if db_healthy else "disconnected",
        },
        "ai": {
            "active_provider": active_provider,
            "provider_statuses": provider_statuses,
        },
        "worker": {
            "is_running": research_job_manager.is_running(),
            "max_workers": research_job_manager.max_workers,
            "active_tasks": research_job_manager.active_worker_count(),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db)):
    total_persons = db.query(func.count(Person.id)).scalar() or 0
    total_jobs = db.query(func.count(ResearchJob.id)).scalar() or 0
    completed_jobs = db.query(func.count(ResearchJob.id)).filter(ResearchJob.status == "completed").scalar() or 0
    total_sources = db.query(func.count(Source.id)).scalar() or 0
    total_evidence = db.query(func.count(Evidence.id)).scalar() or 0
    total_dossiers = db.query(func.count(Dossier.id)).scalar() or 0

    accounting_summary = ai_accounting.get_summary()

    return {
        "platform": {
            "total_persons": total_persons,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "total_sources": total_sources,
            "total_evidence": total_evidence,
            "total_dossiers": total_dossiers,
        },
        "ai_accounting": accounting_summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
