from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob
from backend.app.models.research_query import ResearchQuery
from backend.app.models.research_result import ResearchResult
from backend.app.models.source import Source
from backend.app.repositories.research_repository import ResearchRepository
from backend.app.services.captured_evidence_extractor import (
    CapturedEvidenceExtractor,
)
from backend.app.services.groq_service import GroqService
from backend.app.services.source_capture import SourceCaptureService

from engine.research.citations import CitationExtractor
from engine.research.schemas import ResearchResponse, SearchResult
from engine.research.search.multi_source_router import multi_source_search


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResearchExecutionService:
    """
    Executes browser-backed research queries and persists the complete
    research trail.

    Stage 50 adds:
    - query normalization
    - persistent result caching
    - cache TTL
    - duplicate-result prevention
    - reuse of previously captured sources
    - evidence generation for the current person
    """

    def __init__(
        self,
        db: Session,
        groq_service: Optional[GroqService] = None,
        repository: Optional[ResearchRepository] = None,
        citation_extractor: Optional[CitationExtractor] = None,
        source_capture_service: Optional[SourceCaptureService] = None,
        evidence_extractor: Optional[CapturedEvidenceExtractor] = None,
        cache_ttl_seconds: Optional[int] = None,
        enable_cache: bool = True,
    ):
        self.db = db
        self.groq = groq_service or GroqService()
        self.repository = repository or ResearchRepository(db)
        self.citation_extractor = (
            citation_extractor or CitationExtractor()
        )
        self.source_capture_service = (
            source_capture_service or SourceCaptureService()
        )
        self.evidence_extractor = (
            evidence_extractor or CapturedEvidenceExtractor()
        )

        settings = get_settings()

        self.cache_ttl_seconds = (
            cache_ttl_seconds
            if cache_ttl_seconds is not None
            else settings.research_cache_ttl_seconds
        )

        self.enable_cache = enable_cache

    @staticmethod
    def normalize_query(query_text: str) -> str:
        """
        Normalize a research query for cache comparison.
        """
        return " ".join(query_text.strip().lower().split())

    def _find_cached_query(
        self,
        query_text: str,
    ) -> Optional[ResearchQuery]:
        """
        Find a recently completed identical query.

        ResearchQuery currently does not have a dedicated cache-key column,
        so normalization is performed in Python. Stage 51 can introduce a
        dedicated indexed cache key when PostgreSQL/Supabase becomes the
        production database.
        """
        if not self.enable_cache:
            return None

        normalized_target = self.normalize_query(query_text)

        if not normalized_target:
            return None

        cutoff = datetime.now(timezone.utc) - timedelta(
            seconds=self.cache_ttl_seconds
        )

        candidates = (
            self.db.query(ResearchQuery)
            .filter(ResearchQuery.status == "completed")
            .order_by(ResearchQuery.id.desc())
            .limit(1000)
            .all()
        )

        for candidate in candidates:
            if candidate.id is None:
                continue

            executed_at = getattr(candidate, "executed_at", None)

            if executed_at is not None and executed_at < cutoff:
                continue

            if (
                self.normalize_query(candidate.query_text)
                == normalized_target
            ):
                return candidate

        return None

    def _copy_cached_results(
        self,
        cached_query: ResearchQuery,
        new_query: ResearchQuery,
    ) -> list[SearchResult]:
        """
        Copy cached ResearchResult rows into the new ResearchQuery.
        Source records themselves remain shared and deduplicated.
        """
        cached_results = (
            self.db.query(ResearchResult)
            .filter(
                ResearchResult.research_query_id
                == cached_query.id
            )
            .order_by(ResearchResult.result_rank.asc())
            .all()
        )

        results: list[SearchResult] = []

        for cached_result in cached_results:
            source = (
                self.db.query(Source)
                .filter(Source.id == cached_result.source_id)
                .first()
            )

            if source is None:
                continue

            existing = (
                self.db.query(ResearchResult)
                .filter(
                    ResearchResult.research_query_id == new_query.id,
                    ResearchResult.source_id == source.id,
                )
                .first()
            )

            if existing is None:
                copied = ResearchResult(
                    research_query_id=new_query.id,
                    source_id=source.id,
                    result_rank=cached_result.result_rank,
                    title=cached_result.title,
                    url=cached_result.url,
                    snippet=cached_result.snippet,
                    relevance_score=cached_result.relevance_score,
                    discovery_method="cache",
                    status="cached",
                )

                self.db.add(copied)

            results.append(
                SearchResult(
                    title=source.title or cached_result.title or source.url,
                    url=source.url,
                    snippet=cached_result.snippet,
                    source_domain=(
                        source.url.split("/")[2]
                        if "://" in source.url
                        else None
                    ),
                    result_rank=cached_result.result_rank,
                    discovery_method="cache",
                    relevance_score=cached_result.relevance_score,
                )
            )

        self.db.flush()

        return results

    def _process_sources_and_evidence(
        self,
        research_job: ResearchJob,
        person: Person,
        results: list[SearchResult],
    ) -> tuple[int, int]:
        """
        Ensure every source has a capture and generate evidence for the
        current person.
        """
        source_ids: set[int] = set()

        for result in results:
            source = self.repository.get_or_create_source(result)

            if source.id is None:
                self.db.flush()

            source_ids.add(source.id)

            capture = self.source_capture_service.capture(
                db=self.db,
                source=source,
            )

            if capture.capture_status != "captured":
                continue

            self.evidence_extractor.extract(
                db=self.db,
                person=person,
                source=source,
                capture=capture,
            )

        source_count = len(source_ids)

        evidence_count = (
            self.db.query(Evidence)
            .filter(Evidence.person_id == person.id)
            .count()
        )

        research_job.query_count = (
            self.db.query(ResearchQuery)
            .filter(
                ResearchQuery.research_job_id
                == research_job.id
            )
            .count()
        )

        research_job.source_count = source_count
        research_job.evidence_count = evidence_count

        return source_count, evidence_count

    def _execute_live_search(
        self,
        research_job: ResearchJob,
        person: Person,
        query: ResearchQuery,
        query_text: str,
        max_completion_tokens: int,
    ) -> ResearchResponse:
        """
        Execute live search via Groq browser search or resilient multi-source search fallback.
        """
        search_results: list[SearchResult] = []
        try:
            response = self.groq.client.chat.completions.create(
                model=self.groq.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the PERSONA-X research engine. "
                            "Research only publicly available information. "
                            "Prefer primary and authoritative sources. "
                            "Do not invent facts or sources. "
                            "Distinguish documented facts from claims, "
                            "allegations, and inference."
                        ),
                    },
                    {
                        "role": "user",
                        "content": query_text,
                    },
                ],
                tools=[{"type": "browser_search"}],
                tool_choice="required",
                temperature=0,
                max_completion_tokens=max_completion_tokens,
            )

            message = response.choices[0].message
            citations = self.citation_extractor.extract(message)

            search_results = [
                SearchResult(
                    title=citation.title or citation.url,
                    url=citation.url,
                    snippet=citation.content,
                    source_domain=citation.source_domain,
                    result_rank=citation.result_rank,
                    discovery_method=(
                        citation.discovery_methods[0]
                        if citation.discovery_methods
                        else "browser_search"
                    ),
                )
                for citation in citations
            ]
        except Exception:
            # Fall back to high-authority multi-source search router (Wikipedia, Wikidata, OpenAlex, Web)
            fallback_items = multi_source_search.search(
                query=query_text,
                profession_context=getattr(query, "profession_context", None),
                topic=getattr(query, "topic", None),
                max_results=8,
            )
            search_results = [
                SearchResult(
                    title=item.title,
                    url=item.url,
                    snippet=item.snippet,
                    source_domain=item.source_domain,
                    result_rank=item.result_rank,
                    discovery_method=item.discovery_method,
                    relevance_score=item.relevance_score,
                )
                for item in fallback_items
            ]

        research_response = ResearchResponse(
            query=query_text,
            results=search_results,
            search_status="completed" if search_results else "empty",
            error=None if search_results else "No relevant search results found across sources.",
        )

        for result in research_response.results:
            source = self.repository.get_or_create_source(result)

            existing_result = (
                self.db.query(ResearchResult)
                .filter(
                    ResearchResult.research_query_id == query.id,
                    ResearchResult.source_id == source.id,
                )
                .first()
            )

            if existing_result is None:
                self.db.add(
                    ResearchResult(
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
                )

        return research_response

    def execute(
        self,
        research_job: ResearchJob,
        person: Person,
        query_text: str,
        profession_context=None,
        topic=None,
        priority: int = 5,
        max_completion_tokens: int = 4096,
    ) -> ResearchResponse:
        if not query_text or not query_text.strip():
            raise ValueError("Research query cannot be empty.")

        if research_job.person_id != person.id:
            raise ValueError(
                "Research job does not belong to the supplied Person."
            )

        query_text = query_text.strip()

        query = self.repository.create_query(
            research_job_id=research_job.id,
            query_text=query_text,
            query_type="browser_search",
            profession_context=profession_context,
            topic=topic,
            priority=priority,
        )

        try:
            cached_query = self._find_cached_query(query_text)

            if (
                cached_query is not None
                and cached_query.id != query.id
            ):
                results = self._copy_cached_results(
                    cached_query=cached_query,
                    new_query=query,
                )

                query.result_count = len(results)
                query.status = "completed"

                if hasattr(query, "executed_at"):
                    query.executed_at = datetime.now(timezone.utc)

                source_count, evidence_count = (
                    self._process_sources_and_evidence(
                        research_job=research_job,
                        person=person,
                        results=results,
                    )
                )

                research_job.current_stage = "source_processing"

                self.db.commit()

                return ResearchResponse(
                    query=query_text,
                    results=results,
                    search_status="cached",
                    error=None,
                )

            research_response = self._execute_live_search(
                research_job=research_job,
                person=person,
                query=query,
                query_text=query_text,
                max_completion_tokens=max_completion_tokens,
            )

            query.result_count = len(research_response.results)
            query.status = "completed"

            if hasattr(query, "executed_at"):
                query.executed_at = datetime.now(timezone.utc)

            self.db.flush()

            source_count, evidence_count = (
                self._process_sources_and_evidence(
                    research_job=research_job,
                    person=person,
                    results=research_response.results,
                )
            )

            research_job.current_stage = "source_processing"

            self.db.commit()

            return research_response

        except Exception as exc:
            query.status = "failed"
            query.execution_error = str(exc)

            research_job.status = "failed"
            research_job.current_stage = "research"
            research_job.error_message = str(exc)

            self.db.commit()

            return ResearchResponse(
                query=query_text,
                results=[],
                search_status="error",
                error=str(exc),
            )