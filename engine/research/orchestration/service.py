from typing import Iterable, Optional

from engine.research.orchestration.orchestrator import (
    RegisteredStage,
    ResearchOrchestrator,
)
from engine.research.orchestration.schemas import (
    ResearchPipelineResult,
)


class ResearchOrchestrationService:
    """
    Public service facade for executing PERSONA-X research jobs.

    Service construction is dependency-injected so the existing
    research engines can be connected without coupling the orchestrator
    to a particular implementation.
    """

    def __init__(
        self,
        stages: Optional[Iterable[RegisteredStage]] = None,
    ) -> None:

        self.orchestrator = ResearchOrchestrator(
            stages=stages,
        )

    def register_stage(
        self,
        name: str,
        handler,
        required: bool = True,
    ) -> None:

        self.orchestrator.register(
            name=name,
            handler=handler,
            required=required,
        )

    def run(
        self,
        person_name: str,
        research_job_id: Optional[int] = None,
    ) -> ResearchPipelineResult:

        return self.orchestrator.run(
            person_name=person_name,
            research_job_id=research_job_id,
        )

    def registered_stages(self) -> list[str]:
        return self.orchestrator.registered_stages()