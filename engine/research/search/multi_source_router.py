from typing import Dict, List, Set
from urllib.parse import urlparse

from engine.research.search.base import (
    BaseSearchAdapter,
    SearchQuerySpec,
    UnifiedSearchResult,
)
from engine.research.search.academic_adapter import AcademicSearchAdapter
from engine.research.search.duckduckgo_adapter import DuckDuckGoSearchAdapter
from engine.research.search.wikidata_adapter import WikidataSearchAdapter
from engine.research.search.wikipedia_adapter import WikipediaSearchAdapter
from backend.app.utils.security import is_safe_url, sanitize_search_query


class MultiSourceSearchRouter:
    """
    Intelligent multi-source search engine router.
    Orchestrates queries across Wikipedia, Wikidata, academic repositories, and open web.
    """

    def __init__(self):
        self.wikipedia = WikipediaSearchAdapter()
        self.wikidata = WikidataSearchAdapter()
        self.academic = AcademicSearchAdapter()
        self.web = DuckDuckGoSearchAdapter()

    def search(
        self,
        query: str,
        profession_context: str | None = None,
        topic: str | None = None,
        max_results: int = 15,
    ) -> List[UnifiedSearchResult]:
        sanitized = sanitize_search_query(query)
        if not sanitized:
            return []

        spec = SearchQuerySpec(
            query=sanitized,
            max_results=max_results,
            profession_context=profession_context,
            topic=topic,
        )

        all_results: List[UnifiedSearchResult] = []
        seen_urls: Set[str] = set()

        def add_results(items: List[UnifiedSearchResult]):
            for item in items:
                norm_url = item.url.strip().rstrip("/")
                if norm_url in seen_urls:
                    continue
                if not is_safe_url(item.url):
                    continue
                seen_urls.add(norm_url)
                all_results.append(item)

        # 1. Encyclopedic and Knowledge Base discovery (always high priority for grounding)
        add_results(self.wikipedia.search(spec))
        add_results(self.wikidata.search(spec))

        # 2. Domain-specific search (e.g. academic for scientists/scholars)
        if profession_context in {"scientist", "academic", "researcher"}:
            add_results(self.academic.search(spec))

        # 3. Open Web search for fresh news, interviews, and verified records
        add_results(self.web.search(spec))

        # Sort by tier (Tier 1 official/encyclopedic first) and relevance
        all_results.sort(key=lambda r: (r.source_tier, -r.relevance_score))

        # Re-assign ranks
        for idx, item in enumerate(all_results, start=1):
            item.result_rank = idx

        return all_results[:max_results]


multi_source_search = MultiSourceSearchRouter()
