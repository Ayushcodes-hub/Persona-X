from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ResearchCreateRequest(BaseModel):
    person_name: str = Field(min_length=1, max_length=300)
    requested_scope: Optional[Dict[str, Any]] = None


class ResearchCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    person_id: int
    person_name: str
    status: str
    current_stage: Optional[str] = None
    created_at: Optional[datetime] = None


class ResearchStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    person_id: int
    person_name: str
    status: str
    requested_scope: Optional[Dict[str, Any]] = None
    query_count: int = 0
    source_count: int = 0
    evidence_count: int = 0
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DossierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dossier_id: int
    person_id: int
    research_job_id: Optional[int] = None
    version: int
    status: str
    title: Optional[str] = None
    executive_summary: Optional[str] = None
    dossier_content: Optional[str] = None
    source_count: int = 0
    evidence_count: int = 0
    completeness_score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ErrorResponse(BaseModel):
    detail: str