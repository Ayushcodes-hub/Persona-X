import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import get_settings
from backend.app.models import Base
from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.models.research_query import ResearchQuery
from backend.app.models.research_result import ResearchResult
from backend.app.models.source import Source
from backend.app.models.source_capture import SourceCapture
from backend.app.services.research_execution import ResearchExecutionService


@pytest.mark.live_service
def test_real_browser_research_execution():
    settings = get_settings()

    assert settings.groq_api_key, "GROQ_API_KEY is not configured."

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

    db = SessionLocal()

    try:
        person = Person(
            canonical_name="Jasprit Bumrah",
            identity_status="resolved",
            identity_confidence=1.0,
            primary_profession="athlete",
        )

        db.add(person)
        db.flush()

        job = ResearchJob(
            person_id=person.id,
            job_type="full_research",
            status="running",
            requested_scope={
                "stage": "48C",
                "mode": "real_browser_search",
            },
            query_count=0,
            source_count=0,
            evidence_count=0,
            current_stage="research",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        service = ResearchExecutionService(db=db)

        response = service.execute(
            research_job=job,
            person=person,
            query_text=(
                "Jasprit Bumrah official biography career profile "
                "BCCI India cricket"
            ),
            profession_context="athlete",
            topic="career",
        )

        assert response.search_status == "completed", response.error
        assert response.error is None

        queries = db.query(ResearchQuery).all()
        results = db.query(ResearchResult).all()
        sources = db.query(Source).all()
        captures = db.query(SourceCapture).all()
        evidence = db.query(Evidence).all()

        print()
        print("==============================================")
        print("PERSONA-X STAGE 48C REAL RESEARCH")
        print("==============================================")
        print(f"SEARCH STATUS: {response.search_status}")
        print(f"RESPONSE RESULTS: {len(response.results)}")
        print(f"RESEARCH QUERIES: {len(queries)}")
        print(f"RESEARCH RESULTS: {len(results)}")
        print(f"SOURCES: {len(sources)}")
        print(f"SOURCE CAPTURES: {len(captures)}")
        print(f"EVIDENCE: {len(evidence)}")
        print(f"JOB QUERY COUNT: {job.query_count}")
        print(f"JOB SOURCE COUNT: {job.source_count}")
        print(f"JOB EVIDENCE COUNT: {job.evidence_count}")
        print(f"JOB STAGE: {job.current_stage}")
        print("==============================================")

        assert len(queries) == 1
        assert queries[0].status == "completed"

        assert len(results) > 0
        assert len(sources) > 0

        assert job.query_count == 1
        assert job.source_count > 0

        print("REAL BROWSER RESEARCH: PASS")

    finally:
        db.close()
        engine.dispose()