from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.models.research_query import ResearchQuery
from backend.app.models.research_result import ResearchResult
from backend.app.models.source import Source
from backend.app.models.source_capture import SourceCapture

from engine.research.orchestration.runtime import ResearchOrchestrationRuntime
from engine.identity.schemas import IdentityCandidate


class FakeResearchExecutionService:
    """
    Deterministic Stage 49 research executor.

    This deliberately avoids another live Groq/browser call.
    Stage 48C already verified the real research path.

    Stage 49 validates that persisted research can flow through the
    complete downstream pipeline.
    """

    def __init__(self, db):
        self.db = db

    def execute(
        self,
        research_job,
        person,
        query_text,
        profession_context=None,
        topic=None,
        priority=5,
        max_completion_tokens=4096,
    ):
        query = ResearchQuery(
            research_job_id=research_job.id,
            query_text=query_text,
            query_type="browser_search",
            profession_context=profession_context,
            topic=topic,
            priority=priority,
            status="completed",
            result_count=1,
        )

        self.db.add(query)
        self.db.flush()

        source = Source(
            url="https://example.gov/persona-x-stage49",
            title="Official Stage 49 Test Source",
            publisher="Example Government",
            source_type="official",
            source_tier=1,
            reliability_score=0.98,
            is_verified=True,
        )

        self.db.add(source)
        self.db.flush()

        result = ResearchResult(
            research_query_id=query.id,
            source_id=source.id,
            result_rank=1,
            title="Official Stage 49 Test Source",
            url=source.url,
            snippet=(
                "Example source documenting the person's professional "
                "career and public activity."
            ),
            relevance_score=0.98,
            discovery_method="browser_search",
            status="discovered",
        )

        self.db.add(result)

        capture = SourceCapture(
            source_id=source.id,
            capture_version=1,
            retrieved_at=datetime.now(timezone.utc),
            http_status=200,
            content_type="text/html",
            content_hash="stage49-test-hash",
            extracted_text=(
                "The person began a professional career in cricket. "
                "The person represented the national team and recorded "
                "documented professional achievements."
            ),
            capture_status="captured",
        )

        self.db.add(capture)
        self.db.flush()

        evidence = Evidence(
            person_id=person.id,
            source_id=source.id,
            evidence_type="source_passage",
            verification_status="verified",
            extracted_text=(
                "The person began a professional career in cricket. "
                "The person represented the national team and recorded "
                "documented professional achievements."
            ),
            normalized_claim=(
                "The person had a documented professional cricket career."
            ),
            source_locator=f"capture:{capture.id};paragraph:1",
            confidence=0.95,
            extraction_method="stage49_test_fixture",
            extraction_model=None,
        )

        self.db.add(evidence)
        self.db.flush()

        self.db.commit()

        research_job.query_count = 1
        research_job.source_count = 1
        research_job.evidence_count = 1

        return SimpleNamespace(
            query=query_text,
            results=[
                SimpleNamespace(
                    title=source.title,
                    url=source.url,
                    snippet=result.snippet,
                    source_domain="example.gov",
                    result_rank=1,
                    discovery_method="browser_search",
                    relevance_score=0.98,
                )
            ],
            search_status="completed",
            error=None,
        )


class FakePlanningService:
    """
    Minimal deterministic planner for the Stage 49 integration test.

    The real planning service was already tested in Stage 38.
    This fixture isolates Stage 49 orchestration and persistence.
    """

    def __init__(self):
        self.identity_resolution = None

    def resolve_identity(self, person_name, candidates):
        from engine.identity.resolver import IdentityResolver

        return IdentityResolver().resolve(
            query_name=person_name,
            candidates=candidates,
        )

    def build_plan(self, person_name, professions=None, candidates=None):
        from engine.research.planning_service import ResearchPlanningService

        real_service = ResearchPlanningService()

        return real_service.build_plan(
            person_name=person_name,
            professions=professions,
            candidates=candidates,
        )


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def create_fixture(db):
    person = Person(
        canonical_name="Jasprit Bumrah",
        primary_profession="athlete",
        identity_status="resolved",
        identity_confidence=0.95,
    )

    db.add(person)
    db.flush()

    job = ResearchJob(
        person_id=person.id,
        job_type="full_research",
        status="queued",
        requested_scope={
            "scope": "comprehensive",
            "stage": "49",
        },
        query_count=0,
        source_count=0,
        evidence_count=0,
        current_stage="queued",
    )

    db.add(job)
    db.commit()

    candidate = IdentityCandidate(
        name="Jasprit Bumrah",
        profession="athlete",
        nationality="Indian",
        organization="India national cricket team",
        match_score=1.0,
        confidence=0.95,
    )

    return person, job, candidate


def test_stage49_full_end_to_end(db):
    person, job, candidate = create_fixture(db)

    runtime = ResearchOrchestrationRuntime(
        db=db,
        research_execution_service=FakeResearchExecutionService(db),
        planning_service=FakePlanningService(),
        identity_candidates=[candidate],
        max_queries=1,
    )

    result = runtime.run(research_job_id=job.id)

    print()
    print("=" * 70)
    print("PERSONA-X STAGE 49 END-TO-END")
    print("=" * 70)

    print("PIPELINE STATUS:", result.status)
    print("CURRENT STAGE:", result.current_stage)
    print("COMPLETED STAGES:", result.completed_stages)
    print("FAILED STAGES:", result.failed_stages)

    refreshed_job = (
        db.query(ResearchJob)
        .filter(ResearchJob.id == job.id)
        .first()
    )

    print("JOB STATUS:", refreshed_job.status)
    print("JOB CURRENT STAGE:", refreshed_job.current_stage)
    print("JOB QUERY COUNT:", refreshed_job.query_count)
    print("JOB SOURCE COUNT:", refreshed_job.source_count)
    print("JOB EVIDENCE COUNT:", refreshed_job.evidence_count)

    print(
        "DATABASE QUERIES:",
        db.query(ResearchQuery)
        .filter(ResearchQuery.research_job_id == job.id)
        .count(),
    )

    print("DATABASE SOURCES:", db.query(Source).count())
    print("DATABASE RESULTS:", db.query(ResearchResult).count())
    print("DATABASE CAPTURES:", db.query(SourceCapture).count())
    print(
        "DATABASE EVIDENCE:",
        db.query(Evidence)
        .filter(Evidence.person_id == person.id)
        .count(),
    )

    print("=" * 70)

    assert result.status == "completed"

    assert "identity" in result.completed_stages
    assert "planning" in result.completed_stages
    assert "research" in result.completed_stages
    assert "source_processing" in result.completed_stages
    assert "extraction" in result.completed_stages
    assert "analysis" in result.completed_stages
    assert "profession" in result.completed_stages
    assert "political" in result.completed_stages
    assert "evidence_graph" in result.completed_stages
    assert "dossier" in result.completed_stages

    assert result.failed_stages == []

    assert refreshed_job is not None
    assert refreshed_job.status == "completed"
    assert refreshed_job.current_stage == "dossier"

    assert refreshed_job.query_count >= 1
    assert refreshed_job.source_count >= 1
    assert refreshed_job.evidence_count >= 1

    assert (
        db.query(ResearchQuery)
        .filter(ResearchQuery.research_job_id == job.id)
        .count()
        >= 1
    )

    assert db.query(Source).count() >= 1
    assert db.query(ResearchResult).count() >= 1
    assert db.query(SourceCapture).count() >= 1

    assert (
        db.query(Evidence)
        .filter(Evidence.person_id == person.id)
        .count()
        >= 1
    )

    assert result.context.dossier is not None

    print("STAGE 49: PASS")


def test_stage49_real_runtime_registers_all_downstream_stages(db):
    person, job, candidate = create_fixture(db)

    runtime = ResearchOrchestrationRuntime(
        db=db,
        research_execution_service=FakeResearchExecutionService(db),
        planning_service=FakePlanningService(),
        identity_candidates=[candidate],
        max_queries=1,
    )

    registered = runtime.registered_stages()

    stage_names = [stage.name for stage in registered]

    print()
    print("REGISTERED STAGE 49 RUNTIME STAGES:")
    print(stage_names)

    expected = [
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
    ]

    assert stage_names == expected


def test_stage49_job_counters_are_persisted(db):
    person, job, candidate = create_fixture(db)

    runtime = ResearchOrchestrationRuntime(
        db=db,
        research_execution_service=FakeResearchExecutionService(db),
        planning_service=FakePlanningService(),
        identity_candidates=[candidate],
        max_queries=1,
    )

    result = runtime.run(research_job_id=job.id)

    assert result.status == "completed"

    persisted_job = (
        db.query(ResearchJob)
        .filter(ResearchJob.id == job.id)
        .first()
    )

    assert persisted_job.query_count >= 1
    assert persisted_job.source_count >= 1
    assert persisted_job.evidence_count >= 1
    assert persisted_job.status == "completed"
    assert persisted_job.current_stage == "dossier"


if __name__ == "__main__":
    pytest.main([__file__, "-s"])