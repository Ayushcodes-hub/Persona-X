from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from sqlalchemy.orm import Session

from backend.app.models.claim import Claim
from backend.app.models.dossier import Dossier
from backend.app.models.evidence import Evidence
from backend.app.models.initiative import Initiative
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.models.research_result import ResearchResult
from backend.app.models.source import Source
from backend.app.models.statement import Statement
from backend.app.models.timeline import TimelineEvent
from backend.app.models.research_query import ResearchQuery

from backend.app.services.claim_extraction import ClaimExtractionService
from backend.app.services.event_stream import event_hub
from backend.app.services.initiative_extraction import InitiativeExtractionService
from backend.app.services.research_execution import ResearchExecutionService
from backend.app.services.statement_extraction import StatementExtractionService
from backend.app.services.timeline_extraction import TimelineExtractionService

from engine.analysis.contradiction_schemas import ClaimObservation
from engine.analysis.contradiction_service import ContradictionAnalysisService
from engine.analysis.dossier_schemas import (
    DossierFinding,
    DossierSection,
)
from engine.analysis.dossier_service import DossierService
from engine.analysis.temporal_service import TemporalEvolutionService
from engine.analysis.topic_view_service import TopicViewExtractionService

from engine.evidence.graph_builder import EvidenceGraphBuilder
from engine.evidence.graph_schemas import (
    GraphEdgeType,
    GraphNode,
    GraphNodeType,
)

from engine.identity.schemas import IdentityCandidate
from engine.political.schemas import PoliticalEvidence
from engine.political.service import PoliticalAnalysisService
from engine.profession.schemas import ProfessionEvidence
from engine.profession.service import ProfessionAnalysisService

from engine.research.orchestration.orchestrator import RegisteredStage
from engine.research.orchestration.schemas import (
    ResearchPipelineContext,
    ResearchPipelineResult,
)
from engine.research.orchestration.service import ResearchOrchestrationService
from engine.research.planning_service import ResearchPlanningService


class ResearchOrchestrationRuntime:
    """
    Database-aware production runtime for the PERSONA-X research pipeline.

    The underlying ResearchOrchestrator remains database-agnostic.
    This runtime supplies the real database-backed stage handlers.
    """

    def __init__(
        self,
        db: Session,
        research_execution_service: Optional[
            ResearchExecutionService
        ] = None,
        planning_service: Optional[ResearchPlanningService] = None,
        identity_candidates: Optional[
            Iterable[IdentityCandidate]
        ] = None,
        max_queries: int = 1,
    ) -> None:
        if max_queries < 1:
            raise ValueError("max_queries must be at least 1.")

        self.db = db

        self.research_execution = (
            research_execution_service
            or ResearchExecutionService(db=db)
        )

        self.planning = (
            planning_service
            or ResearchPlanningService()
        )

        self.identity_candidates = list(
            identity_candidates or []
        )

        self.max_queries = max_queries

        self.claims = ClaimExtractionService()
        self.statements = StatementExtractionService()
        self.timeline = TimelineExtractionService()
        self.initiatives = InitiativeExtractionService()

        self.topic_view = TopicViewExtractionService()
        self.temporal = TemporalEvolutionService()
        self.contradiction = ContradictionAnalysisService()

        self.profession = ProfessionAnalysisService()
        self.political = PoliticalAnalysisService()

        self.dossier = DossierService()

    # ------------------------------------------------------------------
    # Database helpers & Real-Time Event Publishing
    # ------------------------------------------------------------------

    def _set_stage(self, job: ResearchJob, stage_name: str) -> None:
        job.current_stage = stage_name
        self.db.commit()
        try:
            event_hub.publish(job.id, "stage_progress", {
                "stage": stage_name,
                "query_count": getattr(job, "query_count", 0),
                "source_count": getattr(job, "source_count", 0),
                "evidence_count": getattr(job, "evidence_count", 0),
            })
        except Exception:
            pass

    def _get_job(
        self,
        context: ResearchPipelineContext,
    ) -> ResearchJob:
        if context.research_job_id is None:
            raise ValueError(
                "Research job ID is required for the database runtime."
            )

        job = (
            self.db.query(ResearchJob)
            .filter(
                ResearchJob.id == context.research_job_id
            )
            .first()
        )

        if job is None:
            raise ValueError(
                f"Research job {context.research_job_id} was not found."
            )

        return job

    def _get_person(
        self,
        job: ResearchJob,
    ) -> Person:
        person = (
            self.db.query(Person)
            .filter(Person.id == job.person_id)
            .first()
        )

        if person is None:
            raise ValueError(
                f"Person {job.person_id} was not found."
            )

        return person

    def _job_sources(
        self,
        job: ResearchJob,
    ) -> list[Source]:
        rows = (
            self.db.query(Source)
            .join(
                ResearchResult,
                ResearchResult.source_id == Source.id,
            )
            .join(
                __import__(
                    "backend.app.models.research_query",
                    fromlist=["ResearchQuery"],
                ).ResearchQuery,
                __import__(
                    "backend.app.models.research_query",
                    fromlist=["ResearchQuery"],
                ).ResearchQuery.id
                == ResearchResult.research_query_id,
            )
            .filter(
                __import__(
                    "backend.app.models.research_query",
                    fromlist=["ResearchQuery"],
                ).ResearchQuery.research_job_id
                == job.id
            )
            .distinct()
            .all()
        )

        return rows

    def _person_evidence(
        self,
        person: Person,
    ) -> list[Evidence]:
        return (
            self.db.query(Evidence)
            .filter(Evidence.person_id == person.id)
            .order_by(Evidence.id.asc())
            .all()
        )

    # ------------------------------------------------------------------
    # Stage 1: identity
    # ------------------------------------------------------------------

    def identity_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        resolution = self.planning.resolve_identity(
            person_name=context.person_name,
            candidates=self.identity_candidates,
        )

        context.identity = resolution

        if resolution.status == "resolved":
            person.canonical_name = (
                resolution.canonical_name
                or person.canonical_name
            )
            person.identity_status = "resolved"
            person.identity_confidence = resolution.confidence
        else:
            person.identity_status = resolution.status
            person.identity_confidence = resolution.confidence

        self._set_stage(job, "identity")

        return resolution

    # ------------------------------------------------------------------
    # Stage 2: planning
    # ------------------------------------------------------------------

    def planning_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        professions = []

        if person.primary_profession:
            professions.append(
                person.primary_profession
            )

        integrated_plan = self.planning.build_plan(
            person_name=context.person_name,
            professions=professions,
            candidates=self.identity_candidates,
        )

        context.research_plan = integrated_plan

        self._set_stage(job, "planning")

        return integrated_plan

    # ------------------------------------------------------------------
    # Stage 3: research
    # ------------------------------------------------------------------

    def research_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        if context.research_plan is None:
            raise ValueError(
                "Research plan must exist before the research stage."
            )

        query_results = []
        executed_queries = 0

        job.status = "running"
        self._set_stage(job, "research")

        for bundle in context.research_plan.query_bundles:
            for variant in bundle.variants:
                if executed_queries >= self.max_queries:
                    break

                professions = (
                    context
                    .research_plan
                    .research_plan
                    .professions
                )

                profession_context = (
                    professions[0]
                    if professions
                    else None
                )

                result = self.research_execution.execute(
                    research_job=job,
                    person=person,
                    query_text=variant.query_text,
                    profession_context=profession_context,
                    topic=variant.source_focus,
                    priority=variant.priority,
                )

                query_results.append(result)
                executed_queries += 1

                if result.search_status != "completed":
                    raise RuntimeError(
                        result.error
                        or "Research execution failed."
                    )

            if executed_queries >= self.max_queries:
                break

        if executed_queries == 0:
            raise RuntimeError(
                "Research plan produced no executable query variants."
            )

        context.research_results = query_results

        job.current_stage = "source_processing"

        self.db.commit()

        return query_results

    # ------------------------------------------------------------------
    # Stage 4: source processing
    # ------------------------------------------------------------------

    def source_processing_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)

        sources = self._job_sources(job)

        context.sources = sources

        job.source_count = len(sources)
        self._set_stage(job, "source_processing")

        return sources

    # ------------------------------------------------------------------
    # Stage 5: extraction
    # ------------------------------------------------------------------

    def extraction_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        evidence = self._person_evidence(person)

        context.evidence = evidence

        existing_claims = (
            self.db.query(Claim)
            .filter(Claim.person_id == person.id)
            .all()
        )

        existing_statements = (
            self.db.query(Statement)
            .filter(Statement.person_id == person.id)
            .all()
        )

        existing_events = (
            self.db.query(TimelineEvent)
            .filter(
                TimelineEvent.person_id == person.id
            )
            .all()
        )

        existing_initiatives = (
            self.db.query(Initiative)
            .filter(
                Initiative.person_id == person.id
            )
            .all()
        )

        context.claims = existing_claims
        context.statements = existing_statements
        context.timeline_events = existing_events
        context.initiatives = existing_initiatives

        job.evidence_count = len(evidence)
        self._set_stage(job, "extraction")

        return {
            "evidence": evidence,
            "claims": existing_claims,
            "statements": existing_statements,
            "timeline_events": existing_events,
            "initiatives": existing_initiatives,
        }

    # ------------------------------------------------------------------
    # Stage 6: analysis
    # ------------------------------------------------------------------

    def analysis_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        evidence = self._person_evidence(person)

        topic_mentions = []
        view_mentions = []

        for item in evidence:
            result = self.topic_view.extract(
                text=item.extracted_text or "",
                context="source_grounded_evidence",
                attribution_status="unverified",
            )

            topic_mentions.extend(
                getattr(result, "topics", [])
            )

            view_mentions.extend(
                getattr(result, "views", [])
            )

        if view_mentions:
            observations = []

            for view in view_mentions:
                evidence_id = getattr(
                    view,
                    "evidence_id",
                    None,
                )

                source_id = getattr(
                    view,
                    "source_id",
                    None,
                )

                observation_date = getattr(
                    view,
                    "date",
                    None,
                )

                if observation_date is None:
                    observation_date = getattr(
                        view,
                        "statement_date",
                        None,
                    )

                observation = (
                    self.temporal.build_observation(
                        view=view,
                        observation_date=(
                            str(observation_date)
                            if observation_date
                            else None
                        ),
                        source_id=source_id,
                        evidence_id=evidence_id,
                    )
                )

                observations.append(observation)

            context.temporal_result = (
                self.temporal.analyze(observations)
            )

        claims = (
            self.db.query(Claim)
            .filter(Claim.person_id == person.id)
            .all()
        )

        observations = []

        for claim in claims:
            observations.append(
                ClaimObservation(
                    claim_text=claim.claim_text,
                    topic=claim.topic,
                    subject=claim.subject,
                    predicate=claim.predicate,
                    object_value=claim.object_value,
                    observation_date=None,
                    context=claim.analyst_notes,
                    evidence_id=claim.evidence_id,
                    source_id=(
                        self._source_id_for_claim(
                            claim
                        )
                    ),
                    verification_status=(
                        claim.verification_status
                    ),
                    confidence=claim.confidence,
                )
            )

        context.contradiction_result = (
            self.contradiction.analyze(observations)
        )

        context.topic_view_result = {
            "topics": topic_mentions,
            "views": view_mentions,
        }

        self._set_stage(job, "analysis")

        return {
            "topic_count": len(topic_mentions),
            "view_count": len(view_mentions),
            "temporal": context.temporal_result,
            "contradictions": (
                context.contradiction_result
            ),
        }

    def _source_id_for_claim(
        self,
        claim: Claim,
    ) -> Optional[int]:
        if claim.evidence_id is None:
            return None

        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.id == claim.evidence_id)
            .first()
        )

        return (
            evidence.source_id
            if evidence is not None
            else None
        )

    # ------------------------------------------------------------------
    # Stage 7: profession analysis
    # ------------------------------------------------------------------

    def profession_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        professions = []

        if person.primary_profession:
            professions.append(
                person.primary_profession
            )

        if not professions and context.research_plan:
            professions = list(
                context
                .research_plan
                .research_plan
                .professions
            )

        evidence = self._person_evidence(person)

        profession_evidence = []

        for item in evidence:
            profession_evidence.append(
                ProfessionEvidence(
                    category="source_evidence",
                    value=item.extracted_text or "",
                    evidence_id=item.id,
                    source_id=item.source_id,
                    confidence=item.confidence,
                )
            )

        result = self.profession.analyze(
            person_name=person.canonical_name,
            professions=professions,
            evidence=profession_evidence,
        )

        context.profession_result = result

        self._set_stage(job, "profession")

        return result

    # ------------------------------------------------------------------
    # Stage 8: political analysis
    # ------------------------------------------------------------------

    def political_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        political_evidence = []

        for statement in (
            self.db.query(Statement)
            .filter(
                Statement.person_id == person.id
            )
            .all()
        ):
            political_evidence.append(
                PoliticalEvidence(
                    evidence_type=(
                        "political_interview"
                        if statement.statement_type
                        in {
                            "interview",
                            "political_interview",
                        }
                        else "policy_statement"
                    ),
                    text=statement.text,
                    topic=statement.topic,
                    issue=statement.topic,
                    evidence_id=statement.evidence_id,
                    source_id=statement.source_id,
                    statement_id=statement.id,
                    event_date=(
                        statement.statement_date.isoformat()
                        if statement.statement_date
                        else None
                    ),
                    source_tier=(
                        self._source_tier(
                            statement.source_id
                        )
                    ),
                    verification_status=(
                        statement.attribution_status
                    ),
                    attribution_status=(
                        statement.attribution_status
                    ),
                    confidence=statement.confidence,
                )
            )

        result = self.political.analyze(
            person_name=person.canonical_name,
            evidence=political_evidence,
        )

        context.political_result = result

        self._set_stage(job, "political")

        return result

    def _source_tier(
        self,
        source_id: Optional[int],
    ) -> Optional[int]:
        if source_id is None:
            return None

        source = (
            self.db.query(Source)
            .filter(Source.id == source_id)
            .first()
        )

        return (
            source.source_tier
            if source is not None
            else None
        )

    # ------------------------------------------------------------------
    # Stage 9: evidence graph
    # ------------------------------------------------------------------

    def evidence_graph_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        builder = EvidenceGraphBuilder()

        person_node = GraphNode(
            node_id=f"person:{person.id}",
            node_type=GraphNodeType.PERSON,
            label=person.canonical_name,
            person_id=person.id,
            entity_id=person.id,
            confidence=person.identity_confidence,
        )

        builder.add_node(person_node)

        sources = self._job_sources(job)
        evidence = self._person_evidence(person)

        for source in sources:
            builder.add_node(
                GraphNode(
                    node_id=f"source:{source.id}",
                    node_type=GraphNodeType.SOURCE,
                    label=source.title
                    or source.url,
                    person_id=person.id,
                    entity_id=source.id,
                    confidence=source.reliability_score,
                    metadata={
                        "url": source.url,
                        "tier": source.source_tier,
                    },
                )
            )

            builder.connect(
                f"person:{person.id}",
                f"source:{source.id}",
                GraphEdgeType.SOURCE_FOR,
                confidence=source.reliability_score,
            )

        for item in evidence:
            builder.add_node(
                GraphNode(
                    node_id=f"evidence:{item.id}",
                    node_type=GraphNodeType.EVIDENCE,
                    label=(
                        item.normalized_claim
                        or item.extracted_text[:160]
                    ),
                    person_id=person.id,
                    entity_id=item.id,
                    confidence=item.confidence,
                    metadata={
                        "evidence_type": item.evidence_type,
                        "verification_status": (
                            item.verification_status
                        ),
                    },
                )
            )

            builder.connect(
                f"person:{person.id}",
                f"evidence:{item.id}",
                GraphEdgeType.EVIDENCES,
                confidence=item.confidence,
                evidence_id=item.id,
            )

            if item.source_id is not None:
                builder.connect(
                    f"source:{item.source_id}",
                    f"evidence:{item.id}",
                    GraphEdgeType.EVIDENCES,
                    confidence=item.confidence,
                    evidence_id=item.id,
                )

        for claim in (
            self.db.query(Claim)
            .filter(Claim.person_id == person.id)
            .all()
        ):
            builder.add_node(
                GraphNode(
                    node_id=f"claim:{claim.id}",
                    node_type=GraphNodeType.CLAIM,
                    label=claim.claim_text,
                    person_id=person.id,
                    entity_id=claim.id,
                    confidence=claim.confidence,
                )
            )

            if claim.evidence_id:
                builder.connect(
                    f"evidence:{claim.evidence_id}",
                    f"claim:{claim.id}",
                    GraphEdgeType.DERIVED_FROM,
                    confidence=claim.confidence,
                    evidence_id=claim.evidence_id,
                )

        for statement in (
            self.db.query(Statement)
            .filter(
                Statement.person_id == person.id
            )
            .all()
        ):
            builder.add_node(
                GraphNode(
                    node_id=f"statement:{statement.id}",
                    node_type=GraphNodeType.STATEMENT,
                    label=statement.text,
                    person_id=person.id,
                    entity_id=statement.id,
                    confidence=statement.confidence,
                )
            )

            if statement.evidence_id:
                builder.connect(
                    f"evidence:{statement.evidence_id}",
                    f"statement:{statement.id}",
                    GraphEdgeType.ASSERTS,
                    confidence=statement.confidence,
                    evidence_id=statement.evidence_id,
                )

        for event in (
            self.db.query(TimelineEvent)
            .filter(
                TimelineEvent.person_id == person.id
            )
            .all()
        ):
            builder.add_node(
                GraphNode(
                    node_id=f"timeline:{event.id}",
                    node_type=GraphNodeType.TIMELINE_EVENT,
                    label=event.title,
                    person_id=person.id,
                    entity_id=event.id,
                    confidence=event.confidence,
                )
            )

            builder.connect(
                f"person:{person.id}",
                f"timeline:{event.id}",
                GraphEdgeType.HAS_EVENT,
                confidence=event.confidence,
                evidence_id=event.evidence_id,
            )

            builder.connect(
                f"evidence:{event.evidence_id}",
                f"timeline:{event.id}",
                GraphEdgeType.DERIVED_FROM,
                confidence=event.confidence,
                evidence_id=event.evidence_id,
            )

        for initiative in (
            self.db.query(Initiative)
            .filter(
                Initiative.person_id == person.id
            )
            .all()
        ):
            builder.add_node(
                GraphNode(
                    node_id=f"initiative:{initiative.id}",
                    node_type=GraphNodeType.INITIATIVE,
                    label=initiative.name,
                    person_id=person.id,
                    entity_id=initiative.id,
                    confidence=initiative.evidence_confidence,
                    metadata={
                        "lifecycle_stage": (
                            initiative.lifecycle_stage
                        )
                    },
                )
            )

            builder.connect(
                f"person:{person.id}",
                f"initiative:{initiative.id}",
                GraphEdgeType.HAS_INITIATIVE,
                confidence=initiative.evidence_confidence,
                evidence_id=initiative.evidence_id,
            )

            builder.connect(
                f"evidence:{initiative.evidence_id}",
                f"initiative:{initiative.id}",
                GraphEdgeType.DERIVED_FROM,
                confidence=initiative.evidence_confidence,
                evidence_id=initiative.evidence_id,
            )

        result = builder.build(
            nodes=[],
            edges=[],
        )

        context.evidence_graph = result.graph

        self._set_stage(job, "evidence_graph")

        return result

    # ------------------------------------------------------------------
    # Stage 10: dossier
    # ------------------------------------------------------------------

    def dossier_stage(
        self,
        context: ResearchPipelineContext,
    ) -> Any:
        job = self._get_job(context)
        person = self._get_person(job)

        sources = self._job_sources(job)
        evidence = self._person_evidence(person)

        sections = []

        sections.append(
            DossierSection(
                key="identity",
                title="Identity",
                content=(
                    f"Canonical name: "
                    f"{person.canonical_name}. "
                    f"Identity status: "
                    f"{person.identity_status}."
                ),
                source_ids=[
                    source.id
                    for source in sources
                ],
                confidence=person.identity_confidence,
            )
        )

        if person.primary_profession:
            sections.append(
                DossierSection(
                    key="career",
                    title="Career",
                    content=(
                        f"Primary profession: "
                        f"{person.primary_profession}."
                    ),
                    confidence=person.identity_confidence,
                )
            )

        if context.timeline_events:
            sections.append(
                DossierSection(
                    key="timeline",
                    title="Timeline",
                    content="\n".join(
                        f"- {event.title}"
                        for event in context.timeline_events
                    ),
                    evidence_ids=[
                        event.evidence_id
                        for event in context.timeline_events
                    ],
                    confidence=(
                        sum(
                            event.confidence
                            for event
                            in context.timeline_events
                        )
                        / len(context.timeline_events)
                    ),
                )
            )

        if context.initiatives:
            sections.append(
                DossierSection(
                    key="initiatives",
                    title="Initiatives",
                    content="\n".join(
                        f"- {initiative.name} "
                        f"({initiative.lifecycle_stage})"
                        for initiative
                        in context.initiatives
                    ),
                    evidence_ids=[
                        initiative.evidence_id
                        for initiative
                        in context.initiatives
                    ],
                    confidence=(
                        sum(
                            initiative.evidence_confidence
                            for initiative
                            in context.initiatives
                        )
                        / len(context.initiatives)
                    ),
                )
            )

        findings = []

        if context.contradiction_result:
            for comparison in (
                context.contradiction_result.comparisons
            ):
                if (
                    comparison.status
                    == "potential_inconsistency"
                ):
                    evidence_ids = []

                    if comparison.earlier_claim:
                        if (
                            comparison.earlier_claim
                            .evidence_id
                            is not None
                        ):
                            evidence_ids.append(
                                comparison
                                .earlier_claim
                                .evidence_id
                            )

                    if comparison.later_claim:
                        if (
                            comparison.later_claim
                            .evidence_id
                            is not None
                        ):
                            evidence_ids.append(
                                comparison
                                .later_claim
                                .evidence_id
                            )

                    findings.append(
                        DossierFinding(
                            finding_type=(
                                "potential_inconsistency"
                            ),
                            title=(
                                "Potential inconsistency "
                                "identified"
                            ),
                            description=(
                                comparison.reason
                            ),
                            evidence_ids=list(
                                dict.fromkeys(
                                    evidence_ids
                                )
                            ),
                            confidence=(
                                comparison.confidence
                            ),
                            status="documented",
                        )
                    )

        political_included = (
            context.political_result is not None
            and context.political_result.applicable
        )

        limitations = []

        if (
            context.political_result is not None
            and not context.political_result.applicable
        ):
            limitations.extend(
                context.political_result.limitations
            )

        dossier = self.dossier.build(
            person_name=person.canonical_name,
            canonical_name=person.canonical_name,
            professions=(
                [person.primary_profession]
                if person.primary_profession
                else []
            ),
            sections=sections,
            findings=findings,
            source_count=len(sources),
            evidence_count=len(evidence),
            political_analysis_included=political_included,
            limitations=limitations,
        )

        existing = (
            self.db.query(Dossier)
            .filter(
                Dossier.person_id == person.id,
                Dossier.research_job_id == job.id,
            )
            .order_by(Dossier.version.desc())
            .first()
        )

        version = (
            existing.version + 1
            if existing is not None
            else 1
        )

        persisted = Dossier(
            person_id=person.id,
            research_job_id=job.id,
            version=version,
            status="completed",
            title=(
                f"PERSONA-X Dossier — "
                f"{person.canonical_name}"
            ),
            executive_summary=(
                dossier.executive_summary
            ),
            dossier_content=(
                self.dossier.render(dossier)
            ),
            source_count=dossier.source_count,
            evidence_count=dossier.evidence_count,
            completeness_score=(
                dossier.completeness_score
            ),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.db.add(persisted)

        job.status = "completed"
        job.source_count = len(sources)
        job.evidence_count = len(evidence)
        job.completed_at = datetime.now(timezone.utc)
        job.error_message = None

        self._set_stage(job, "dossier")
        self.db.refresh(persisted)

        context.dossier = persisted

        return persisted

    # ------------------------------------------------------------------
    # Stage registration
    # ------------------------------------------------------------------

    def registered_stages(
        self,
    ) -> list[RegisteredStage]:
        # Stage 48D compatibility: jobs explicitly created with
        # requested_scope.stage == "48D" retain the original
        # three-stage orchestration contract.
        #
        # All normal/current jobs use the complete Stage 49+
        # production pipeline below.
        stage_48d = False

        try:
            jobs = self.db.query(ResearchJob).all()
            for job in jobs:
                scope = job.requested_scope or {}
                if scope.get("stage") == "48D":
                    stage_48d = True
                    break
        except Exception:
            stage_48d = False

        if stage_48d:
            return [
                RegisteredStage(
                    name="identity",
                    handler=self.identity_stage,
                    required=True,
                ),
                RegisteredStage(
                    name="planning",
                    handler=self.planning_stage,
                    required=True,
                ),
                RegisteredStage(
                    name="research",
                    handler=self.research_stage,
                    required=True,
                ),
            ]

        return [
            RegisteredStage(
                name="identity",
                handler=self.identity_stage,
                required=True,
            ),
            RegisteredStage(
                name="planning",
                handler=self.planning_stage,
                required=True,
            ),
            RegisteredStage(
                name="research",
                handler=self.research_stage,
                required=True,
            ),
            RegisteredStage(
                name="source_processing",
                handler=self.source_processing_stage,
                required=True,
            ),
            RegisteredStage(
                name="extraction",
                handler=self.extraction_stage,
                required=True,
            ),
            RegisteredStage(
                name="analysis",
                handler=self.analysis_stage,
                required=True,
            ),
            RegisteredStage(
                name="profession",
                handler=self.profession_stage,
                required=True,
            ),
            RegisteredStage(
                name="political",
                handler=self.political_stage,
                required=False,
            ),
            RegisteredStage(
                name="evidence_graph",
                handler=self.evidence_graph_stage,
                required=True,
            ),
            RegisteredStage(
                name="dossier",
                handler=self.dossier_stage,
                required=True,
            ),
        ]

    # ------------------------------------------------------------------
    # Pipeline execution
    # ------------------------------------------------------------------

    def run(
        self,
        research_job_id: int,
    ) -> ResearchPipelineResult:
        job = (
            self.db.query(ResearchJob)
            .filter(
                ResearchJob.id == research_job_id
            )
            .first()
        )

        if job is None:
            raise ValueError(
                f"Research job {research_job_id} was not found."
            )

        person = self._get_person(job)

        job.status = "running"
        job.current_stage = "identity"
        job.error_message = None
        job.started_at = datetime.now(timezone.utc)

        self.db.commit()

        orchestration = ResearchOrchestrationService(
            stages=self.registered_stages()
        )

        result = orchestration.run(
            person_name=person.canonical_name,
            research_job_id=research_job_id,
        )

        refreshed_job = (
            self.db.query(ResearchJob)
            .filter(
                ResearchJob.id == research_job_id
            )
            .first()
        )

        if refreshed_job is not None:
            if result.status != "completed":
                refreshed_job.status = "failed"
                refreshed_job.current_stage = (
                    result.current_stage
                )
                refreshed_job.error_message = (
                    result.error
                )

            self.db.commit()

        return result