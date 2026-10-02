from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional

from engine.research.orchestration.schemas import (
    ResearchPipelineContext,
    ResearchPipelineResult,
)


StageHandler = Callable[[ResearchPipelineContext], object]


@dataclass
class RegisteredStage:
    name: str
    handler: StageHandler
    required: bool = True


class ResearchOrchestrator:
    """
    Executes the PERSONA-X research pipeline in deterministic stage order.

    Individual research engines remain independent. The orchestrator
    controls lifecycle, ordering, failure handling, and shared context.
    """

    DEFAULT_STAGE_ORDER = (
        "identity",
        "planning",
        "research",
        "source_processing",
        "extraction",
        "analysis",
        "profession",
        "political",
        "evidence_graph",
        "dossier",
    )

    def __init__(
        self,
        stages: Optional[Iterable[RegisteredStage]] = None,
    ) -> None:

        self._stages: Dict[str, RegisteredStage] = {}

        if stages:
            for stage in stages:
                self.register(
                    name=stage.name,
                    handler=stage.handler,
                    required=stage.required,
                )

    def register(
        self,
        name: str,
        handler: StageHandler,
        required: bool = True,
    ) -> None:

        if not name.strip():
            raise ValueError("Stage name cannot be empty.")

        if not callable(handler):
            raise TypeError(
                f"Handler for stage '{name}' must be callable."
            )

        self._stages[name] = RegisteredStage(
            name=name,
            handler=handler,
            required=required,
        )

    def has_stage(self, name: str) -> bool:
        return name in self._stages

    def registered_stages(self) -> list[str]:
        return [
            stage
            for stage in self.DEFAULT_STAGE_ORDER
            if stage in self._stages
        ]

    def run(
        self,
        person_name: str,
        research_job_id: Optional[int] = None,
    ) -> ResearchPipelineResult:

        if not person_name.strip():
            raise ValueError("person_name cannot be empty.")

        context = ResearchPipelineContext(
            person_name=person_name.strip(),
            research_job_id=research_job_id,
            status="running",
        )

        failed_stages: list[str] = []

        for stage_name in self.DEFAULT_STAGE_ORDER:
            stage = self._stages.get(stage_name)

            if stage is None:
                continue

            context.current_stage = stage_name

            try:
                output = stage.handler(context)

                context.record_stage(
                    stage=stage_name,
                    status="completed",
                    data=output,
                )

            except Exception as exc:
                failed_stages.append(stage_name)

                context.status = "failed"
                context.error = (
                    f"{type(exc).__name__}: {exc}"
                )

                context.record_stage(
                    stage=stage_name,
                    status="failed",
                    message=context.error,
                )

                if stage.required:
                    break

        if failed_stages:
            context.status = "failed"

        else:
            context.status = "completed"

        completed_stages = [
            result.stage
            for result in context.stages
            if result.status == "completed"
        ]

        return ResearchPipelineResult(
            person_name=context.person_name,
            status=context.status,
            current_stage=context.current_stage,
            error=context.error,
            context=context,
            completed_stages=completed_stages,
            failed_stages=failed_stages,
        )