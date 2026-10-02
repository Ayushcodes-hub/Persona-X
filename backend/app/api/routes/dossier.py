from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.dossier import Dossier
from backend.app.schemas.research import DossierResponse


router = APIRouter(
    prefix="/dossiers",
    tags=["dossiers"],
)


@router.get(
    "/{dossier_id}",
    response_model=DossierResponse,
)
def get_dossier(
    dossier_id: int,
    db: Session = Depends(get_db),
):
    dossier = (
        db.query(Dossier)
        .filter(Dossier.id == dossier_id)
        .first()
    )

    if dossier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dossier {dossier_id} was not found.",
        )

    return DossierResponse(
        dossier_id=dossier.id,
        person_id=dossier.person_id,
        research_job_id=dossier.research_job_id,
        version=dossier.version,
        status=dossier.status,
        title=dossier.title,
        executive_summary=dossier.executive_summary,
        dossier_content=dossier.dossier_content,
        source_count=dossier.source_count,
        evidence_count=dossier.evidence_count,
        completeness_score=dossier.completeness_score,
        created_at=dossier.created_at,
        updated_at=dossier.updated_at,
    )