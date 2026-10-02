from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

from engine.research.schemas import ResearchResponse, SearchResult


class ResearchIngestionService:
    """Normalize research responses before database persistence."""

    def normalize_url(self, url: str) -> str:
        return url.strip()

    def extract_domain(self, url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() or None
        except Exception:
            return None

    def normalize_result(
        self,
        result: SearchResult,
        rank: int,
    ) -> SearchResult:
        result.url = self.normalize_url(result.url)
        result.source_domain = result.source_domain or self.extract_domain(result.url)
        result.result_rank = result.result_rank or rank
        result.discovery_method = result.discovery_method or "browser_search"
        return result

    def normalize_response(
        self,
        response: ResearchResponse,
    ) -> ResearchResponse:
        normalized: List[SearchResult] = []

        for index, result in enumerate(response.results, start=1):
            normalized.append(self.normalize_result(result, index))

        response.results = normalized
        return response

    def retrieved_at(self) -> datetime:
        return datetime.now(timezone.utc)
