from dataclasses import dataclass
from types import SimpleNamespace

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
from backend.app.services.research_execution import ResearchExecutionService


@dataclass
class FakeCitation:
    title: str
    url: str
    content: str
    source_domain: str
    result_rank: int
    discovery_methods: list


class FakeCitationExtractor:
    def extract(self, message):
        return [
            FakeCitation(
                title="Official Example Source",
                url="https://example.gov/person",
                content=(
                    "This is a sufficiently long source passage containing "
                    "documented public information about the person."
                ),
                source_domain="example.gov",
                result_rank=1,
                discovery_methods=["browser_search"],
            )
        ]


class FakeGroqClient:
    class Chat:
        class Completions:
            def create(self, **kwargs):
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(
                                content="Research response",
                            )
                        )
                    ]
                )

        def __init__(self):
            self.completions = self.Completions()

    def __init__(self):
        self.chat = self.Chat()


class FakeGroqService:
    model = "test-model"

    def __init__(self):
        self.client = FakeGroqClient()


class FakeSourceCaptureService:
    def capture(self, db, source):
        capture = SourceCapture(
            source_id=source.id,
            capture_version=1,
            http_status=200,
            content_type="text/html",
            content_hash="test-hash",
            extracted_text=(
                "This is a sufficiently long source passage containing "
                "documented public information about the person."
            ),
            capture_status="captured",
        )

        db.add(capture)
        db.commit()
        db.refresh(capture)

        return capture


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

    return engine, SessionLocal


def test_research_execution_persists_complete_source_evidence_chain():
    engine, SessionLocal = build_database()
    db = SessionLocal()

    try:
        person = Person(
            canonical_name="Test Person",
            identity_status="resolved",
            identity_confidence=1.0,
        )
        db.add(person)
        db.flush()

        job = ResearchJob(
            person_id=person.id,
            job_type="full_research",
            status="running",
            requested_scope={"test": True},
            query_count=0,
            source_count=0,
            evidence_count=0,
            current_stage="research",
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        service = ResearchExecutionService(
            db=db,
            groq_service=FakeGroqService(),
            citation_extractor=FakeCitationExtractor(),
            source_capture_service=FakeSourceCaptureService(),
        )

        response = service.execute(
            research_job=job,
            person=person,
            query_text="Test Person official biography",
        )

        assert response.search_status == "completed"
        assert response.error is None
        assert len(response.results) == 1

        queries = db.query(ResearchQuery).all()
        assert len(queries) == 1
        assert queries[0].status == "completed"
        assert queries[0].result_count == 1

        results = db.query(ResearchResult).all()
        assert len(results) == 1
        assert results[0].status == "discovered"

        sources = db.query(Source).all()
        assert len(sources) == 1
        assert sources[0].url == "https://example.gov/person"
        assert sources[0].source_tier == 1

        captures = db.query(SourceCapture).all()
        assert len(captures) == 1
        assert captures[0].capture_status == "captured"

        evidence = db.query(Evidence).all()
        assert len(evidence) == 1
        assert evidence[0].person_id == person.id
        assert evidence[0].source_id == sources[0].id
        assert evidence[0].verification_status == "unverified"

        db.refresh(job)

        assert job.query_count == 1
        assert job.source_count == 1
        assert job.evidence_count == 1
        assert job.current_stage == "source_processing"

    finally:
        db.close()
        engine.dispose()