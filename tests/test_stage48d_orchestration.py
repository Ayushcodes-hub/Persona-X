from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from engine.identity.schemas import IdentityCandidate
from engine.research.orchestration.runtime import ResearchOrchestrationRuntime
from engine.research.schemas import ResearchResponse


class FakeResearchExecutionService:
    def __init__(self):
        self.calls = []

    def execute(
        self,
        research_job,
        person,
        query_text,
        profession_context=None,
        topic=None,
        priority=5,
    ):
        self.calls.append(
            {
                "research_job_id": research_job.id,
                "person_id": person.id,
                "query_text": query_text,
                "profession_context": profession_context,
                "topic": topic,
                "priority": priority,
            }
        )

        research_job.query_count += 1

        return ResearchResponse(
            query=query_text,
            results=[],
            search_status="completed",
            error=None,
        )


def build_database():
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

    return SessionLocal()


def test_stage48d_orchestration_runtime():
    db = build_database()

    try:
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
                "stage": "48D",
            },
            query_count=0,
            source_count=0,
            evidence_count=0,
            current_stage="queued",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        identity_candidate = IdentityCandidate(
            name="Jasprit Bumrah",
            profession="athlete",
            match_score=0.75,
            confidence=0.95,
            reasons=[
                "Exact canonical name match.",
                "Profession matches athlete.",
            ],
        )

        fake_execution = FakeResearchExecutionService()

        runtime = ResearchOrchestrationRuntime(
            db=db,
            research_execution_service=fake_execution,
            identity_candidates=[identity_candidate],
            max_queries=1,
        )

        assert [
            stage.name
            for stage in runtime.registered_stages()
        ] == [
            "identity",
            "planning",
            "research",
        ]

        result = runtime.run(
            research_job_id=job.id,
        )

        assert result.status == "completed"

        assert result.completed_stages == [
            "identity",
            "planning",
            "research",
        ]

        assert result.failed_stages == []

        assert result.context.identity is not None
        assert result.context.research_plan is not None
        assert result.context.research_plan.task_count > 0

        assert len(result.context.research_results) == 1

        assert len(fake_execution.calls) == 1

        assert fake_execution.calls[0]["research_job_id"] == job.id
        assert fake_execution.calls[0]["person_id"] == person.id
        assert fake_execution.calls[0]["profession_context"] == "athlete"

        refreshed_job = (
            db.query(ResearchJob)
            .filter(ResearchJob.id == job.id)
            .first()
        )

        assert refreshed_job is not None
        assert refreshed_job.status == "running"
        assert refreshed_job.current_stage == "source_processing"
        assert refreshed_job.query_count == 1
        assert refreshed_job.error_message is None

        refreshed_person = (
            db.query(Person)
            .filter(Person.id == person.id)
            .first()
        )

        assert refreshed_person is not None
        assert refreshed_person.identity_status == "resolved"
        assert refreshed_person.identity_confidence > 0

        print()
        print("=" * 60)
        print("PERSONA-X STAGE 48D")
        print("=" * 60)
        print("ORCHESTRATION STATUS:", result.status)
        print("COMPLETED STAGES:", result.completed_stages)
        print("FAILED STAGES:", result.failed_stages)
        print("IDENTITY STATUS:", result.context.identity.status)
        print(
            "RESEARCH TASK COUNT:",
            result.context.research_plan.task_count,
        )
        print("EXECUTED QUERIES:", len(fake_execution.calls))
        print("JOB STATUS:", refreshed_job.status)
        print("JOB CURRENT STAGE:", refreshed_job.current_stage)
        print("=" * 60)
        print("STAGE 48D: PASS")
        print("=" * 60)

    finally:
        db.close()