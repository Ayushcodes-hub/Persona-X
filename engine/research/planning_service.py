from dataclasses import dataclass
from typing import List, Optional

from engine.identity.context import IdentityContextBuilder
from engine.identity.resolver import IdentityResolver
from engine.identity.schemas import IdentityCandidate, IdentityResolution
from engine.research.planner import UniversalResearchPlanner
from engine.research.planner_schemas import ResearchPlan, ResearchTask
from engine.research.query_generator import ResearchQueryGenerator
from engine.research.query_schemas import QueryBundle


@dataclass
class IntegratedResearchPlan:
    """
    End-to-end planning result.

    This object connects identity resolution, identity context,
    universal research planning, and query generation without
    performing external research itself.
    """

    identity_resolution: IdentityResolution
    identity_context_verified: bool
    research_plan: ResearchPlan
    query_bundles: List[QueryBundle]

    @property
    def task_count(self) -> int:
        return self.research_plan.task_count

    @property
    def query_count(self) -> int:
        return sum(bundle.query_count for bundle in self.query_bundles)


class ResearchPlanningService:
    """
    Coordinates the deterministic research-planning pipeline.

    Pipeline:

        candidates
            ↓
        identity resolution
            ↓
        verified identity context
            ↓
        universal research planner
            ↓
        targeted query generation

    This service does not claim that a person has been correctly
    identified unless the identity resolver itself returns a resolved
    result. It also does not perform external web research.
    """

    def __init__(
        self,
        identity_resolver: Optional[IdentityResolver] = None,
        planner: Optional[UniversalResearchPlanner] = None,
        query_generator: Optional[ResearchQueryGenerator] = None,
        context_builder: Optional[IdentityContextBuilder] = None,
    ):
        self.identity_resolver = (
            identity_resolver or IdentityResolver()
        )
        self.planner = (
            planner or UniversalResearchPlanner()
        )
        self.query_generator = (
            query_generator or ResearchQueryGenerator()
        )
        self.context_builder = (
            context_builder or IdentityContextBuilder()
        )

    def resolve_identity(
        self,
        person_name: str,
        candidates: List[IdentityCandidate],
    ) -> IdentityResolution:
        return self.identity_resolver.resolve(
            query_name=person_name,
            candidates=candidates,
        )

    def build_plan(
        self,
        person_name: str,
        professions: Optional[List[str]] = None,
        candidates: Optional[List[IdentityCandidate]] = None,
    ) -> IntegratedResearchPlan:
        """
        Build a complete research plan.

        If identity candidates are supplied, identity resolution is
        performed first and verified context is propagated downstream.

        If no candidates are supplied, the system deliberately creates
        an unresolved identity result rather than inventing identity data.
        """

        candidates = candidates or []

        identity_resolution = self.resolve_identity(
            person_name=person_name,
            candidates=candidates,
        )

        identity_context = self.context_builder.build(
            identity_resolution
        )

        effective_professions = list(professions or [])

        if (
            identity_context.is_verified
            and identity_context.profession
            and not effective_professions
        ):
            effective_professions = [
                identity_context.profession
            ]

        research_plan = self.planner.build_plan(
            person_name=(
                identity_resolution.canonical_name
                if identity_resolution.status == "resolved"
                and identity_resolution.canonical_name
                else person_name
            ),
            professions=effective_professions,
        )

        query_bundles: List[QueryBundle] = []

        for task in research_plan.tasks:
            bundle = self.query_generator.generate(
                task,
                identity_context=identity_context,
            )
            query_bundles.append(bundle)

        return IntegratedResearchPlan(
            identity_resolution=identity_resolution,
            identity_context_verified=identity_context.is_verified,
            research_plan=research_plan,
            query_bundles=query_bundles,
        )