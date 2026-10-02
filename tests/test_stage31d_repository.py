from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.models import (
    Base,
    Person,
    ResearchJob,
    ResearchResult,
    Source,
)
from backend.app.repositories.research_repository import ResearchRepository
from engine.research.schemas import ResearchResponse, SearchResult


TEST_PERSON_NAME = "PERSONA-X Stage31D Isolated Test"
TEST_QUERY = "Stage 31D isolated source verification test"

TEST_URLS = [
    "https://www.sec.gov/Archives/PERSONA-X-stage31D-isolated",
    "https://www.reuters.com/world/PERSONA-X-stage31D-isolated/",
]


def test_stage31d_repository_source_verification():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(test_engine)

    db = Session(test_engine)

    try:
        person = Person(
            canonical_name=TEST_PERSON_NAME,
            primary_profession="test",
            identity_confidence=1.0,
            identity_status="resolved",
        )
        db.add(person)
        db.flush()

        job = ResearchJob(
            person_id=person.id,
            job_type="research",
            status="pending",
        )
        db.add(job)
        db.flush()

        response = ResearchResponse(
            query=TEST_QUERY,
            results=[
                SearchResult(
                    title="SEC Isolated Test Source",
                    url=TEST_URLS[0],
                    snippet="Primary institutional source test.",
                    source_domain="www.sec.gov",
                    result_rank=1,
                    discovery_method="browser_search",
                    relevance_score=1.0,
                ),
                SearchResult(
                    title="Reuters Isolated Test Source",
                    url=TEST_URLS[1],
                    snippet="Major news source test.",
                    source_domain="www.reuters.com",
                    result_rank=2,
                    discovery_method="browser_search",
                    relevance_score=0.9,
                ),
            ],
            search_status="completed",
        )

        repository = ResearchRepository(db)

        query = repository.persist_response(
            research_job_id=job.id,
            response=response,
            query_text=TEST_QUERY,
            query_type="browser_search",
        )

        db.refresh(query)

        results = (
            db.query(ResearchResult)
            .filter(ResearchResult.research_query_id == query.id)
            .order_by(ResearchResult.result_rank)
            .all()
        )

        sources = [
            db.query(Source)
            .filter(Source.id == result.source_id)
            .first()
            for result in results
        ]

        assert query.status == "completed"
        assert query.result_count == 2

        assert len(results) == 2
        assert len(sources) == 2

        assert results[0].url == TEST_URLS[0]
        assert results[1].url == TEST_URLS[1]

        assert sources[0].source_tier == 1
        assert sources[0].source_type == "primary_institutional"
        assert sources[0].reliability_score == 0.98

        assert sources[1].source_tier == 2
        assert sources[1].source_type == "major_news"
        assert sources[1].reliability_score == 0.95

    finally:
        db.close()
        test_engine.dispose()