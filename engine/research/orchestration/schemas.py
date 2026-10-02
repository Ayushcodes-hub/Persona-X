from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ResearchStageResult:
    stage: str
    status: str = "completed"
    message: Optional[str] = None
    data: Any = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchPipelineContext:
    person_name: str
    research_job_id: Optional[int] = None

    identity: Any = None
    research_plan: Any = None
    research_results: List[Any] = field(default_factory=list)

    sources: List[Any] = field(default_factory=list)
    captures: List[Any] = field(default_factory=list)
    evidence: List[Any] = field(default_factory=list)
    claims: List[Any] = field(default_factory=list)
    statements: List[Any] = field(default_factory=list)
    timeline_events: List[Any] = field(default_factory=list)
    initiatives: List[Any] = field(default_factory=list)

    topic_view_result: Any = None
    temporal_result: Any = None
    contradiction_result: Any = None
    profession_result: Any = None
    political_result: Any = None
    evidence_graph: Any = None
    dossier: Any = None

    stages: List[ResearchStageResult] = field(default_factory=list)

    status: str = "created"
    current_stage: Optional[str] = None
    error: Optional[str] = None

    def record_stage(
        self,
        stage: str,
        status: str = "completed",
        message: Optional[str] = None,
        data: Any = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> ResearchStageResult:

        result = ResearchStageResult(
            stage=stage,
            status=status,
            message=message,
            data=data,
            metrics=metrics or {},
        )

        self.stages.append(result)
        self.current_stage = stage

        return result


@dataclass
class ResearchPipelineResult:
    person_name: str
    status: str
    current_stage: Optional[str]
    error: Optional[str]
    context: ResearchPipelineContext
    completed_stages: List[str]
    failed_stages: List[str]