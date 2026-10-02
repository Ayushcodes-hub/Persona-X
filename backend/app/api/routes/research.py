from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.research_job import ResearchJob
from backend.app.schemas.research import (
    ResearchCreateRequest,
    ResearchCreateResponse,
    ResearchStatusResponse,
)
from backend.app.services.event_stream import event_hub
from backend.app.services.research_api import ResearchAPIService
from backend.app.services.research_worker import research_job_manager


router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "",
    response_model=ResearchCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_research(
    request: ResearchCreateRequest,
    db: Session = Depends(get_db),
):
    job = ResearchAPIService.create_research_job(
        db=db,
        person_name=request.person_name,
        requested_scope=request.requested_scope,
    )

    return ResearchCreateResponse(
        job_id=job.id,
        person_id=job.person_id,
        person_name=request.person_name.strip(),
        status=job.status,
        current_stage=job.current_stage,
        created_at=job.created_at,
    )


@router.post(
    "/{job_id}/run",
    response_model=ResearchStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def run_research(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(ResearchJob)
        .filter(ResearchJob.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    if job.status == "completed":
        raise HTTPException(
            status_code=409,
            detail="Research job is already completed.",
        )

    submitted = research_job_manager.enqueue(
        job_id=job_id,
        force=False,
    )

    refreshed_job = (
        db.query(ResearchJob)
        .filter(ResearchJob.id == job_id)
        .first()
    )

    if refreshed_job is None:
        raise HTTPException(
            status_code=404,
            detail="Research job disappeared after submission.",
        )

    if not submitted and refreshed_job.status not in {
        "queued",
        "running",
    }:
        raise HTTPException(
            status_code=409,
            detail="Research job could not be queued.",
        )

    person = ResearchAPIService.get_person_for_job(
        db=db,
        job=refreshed_job,
    )

    return ResearchStatusResponse(
        job_id=refreshed_job.id,
        person_id=refreshed_job.person_id,
        person_name=(
            person.canonical_name
            if person is not None
            else "Unknown"
        ),
        status=refreshed_job.status,
        requested_scope=refreshed_job.requested_scope,
        query_count=refreshed_job.query_count,
        source_count=refreshed_job.source_count,
        evidence_count=refreshed_job.evidence_count,
        current_stage=refreshed_job.current_stage,
        error_message=refreshed_job.error_message,
        created_at=refreshed_job.created_at,
        updated_at=refreshed_job.updated_at,
    )


@router.get(
    "/{job_id}",
    response_model=ResearchStatusResponse,
)
def get_research_status(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = ResearchAPIService.get_job(
        db=db,
        job_id=job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    person = ResearchAPIService.get_person_for_job(
        db=db,
        job=job,
    )

    return ResearchStatusResponse(
        job_id=job.id,
        person_id=job.person_id,
        person_name=(
            person.canonical_name
            if person is not None
            else "Unknown"
        ),
        status=job.status,
        requested_scope=job.requested_scope,
        query_count=job.query_count,
        source_count=job.source_count,
        evidence_count=job.evidence_count,
        current_stage=job.current_stage,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get(
    "/{job_id}/stream",
)
async def stream_research_progress(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    job = ResearchAPIService.get_job(
        db=db,
        job_id=job_id,
    )
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Research job not found.",
        )

    last_event_id = None
    last_id_hdr = request.headers.get("Last-Event-ID") or request.query_params.get("last_event_id")
    if last_id_hdr:
        try:
            last_event_id = int(last_id_hdr)
        except ValueError:
            last_event_id = None

    return StreamingResponse(
        event_hub.stream(job_id, last_event_id=last_event_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )