from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.research_query import ResearchQuery
from backend.app.models.research_result import ResearchResult
from backend.app.models.source import Source
from engine.research.schemas import ResearchResponse
from engine.research.source_verification import SourceVerifier


class ResearchRepository:
    def __init__(self, db: Session):
        self.db = db
        self.source_verifier = SourceVerifier()

    def create_query(
        self,
        research_job_id: int,
        query_text: str,
        query_type: str = "general_research",
        profession_context: Optional[str] = None,
        topic: Optional[str] = None,
        priority: int = 5,
    ):
        query = ResearchQuery(
            research_job_id=research_job_id,
            query_text=query_text,
            query_type=query_type,
            profession_context=profession_context,
            topic=topic,
            priority=priority,
            status="pending",
        )

        self.db.add(query)
        self.db.flush()

        return query

    def get_or_create_source(self, result):
        source = (
            self.db.query(Source)
            .filter(Source.url == result.url)
            .first()
        )

        verification = self.source_verifier.classify(
            result.url,
            result.title,
        )

        if source is None:
            source = Source(
                url=result.url,
                title=result.title,
                publisher=result.source_domain,
                source_type=verification.source_type,
                source_tier=verification.source_tier,
                reliability_score=verification.confidence,
                is_verified=False,
                description=verification.reason,
            )

            self.db.add(source)
            self.db.flush()

        else:
            source.title = result.title or source.title
            source.publisher = result.source_domain or source.publisher
            source.source_type = verification.source_type
            source.source_tier = verification.source_tier
            source.reliability_score = verification.confidence
            source.description = verification.reason

        return source

    def persist_response(
        self,
        research_job_id: int,
        response: ResearchResponse,
        query_text: str,
        query_type: str = "general_research",
        profession_context: Optional[str] = None,
        topic: Optional[str] = None,
        priority: int = 5,
    ):
        query = self.create_query(
            research_job_id=research_job_id,
            query_text=query_text,
            query_type=query_type,
            profession_context=profession_context,
            topic=topic,
            priority=priority,
        )

        for result in response.results:
            source = self.get_or_create_source(result)

            record = ResearchResult(
                research_query_id=query.id,
                source_id=source.id,
                result_rank=result.result_rank,
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                relevance_score=result.relevance_score,
                discovery_method=result.discovery_method,
                status="discovered",
            )

            self.db.add(record)

        query.result_count = len(response.results)

        query.status = (
            "completed"
            if response.search_status == "completed"
            else "failed"
        )

        self.db.commit()
        self.db.refresh(query)

        return query