from typing import List

import httpx

from engine.research.search.base import BaseSearchAdapter, SearchQuerySpec, UnifiedSearchResult
from backend.app.utils.security import is_safe_url


class AcademicSearchAdapter(BaseSearchAdapter):
    """
    Search OpenAlex API for published papers, citations, and scholarly contributions.
    """

    API_URL = "https://api.openalex.org/works"
    USER_AGENT = "PERSONA-X Research Engine/1.0 (mailto:research@persona-x.ai)"

    @property
    def adapter_name(self) -> str:
        return "openalex_academic"

    def search(self, spec: SearchQuerySpec) -> List[UnifiedSearchResult]:
        query = spec.query.strip()
        if not query:
            return []

        params = {
            "search": query,
            "per_page": min(spec.max_results, 5),
            "sort": "cited_by_count:desc",
        }

        try:
            with httpx.Client(timeout=10.0, headers={"User-Agent": self.USER_AGENT}) as client:
                res = client.get(self.API_URL, params=params)
                if res.status_code != 200:
                    return []
                data = res.json()

            results = []
            for rank, work in enumerate(data.get("results", []), start=1):
                title = work.get("title") or "Scholarly Publication"
                doi = work.get("doi")
                url = doi or work.get("id") or ""

                if not url or not is_safe_url(url):
                    continue

                pub_year = work.get("publication_year")
                cited_by = work.get("cited_by_count", 0)
                venue = (work.get("primary_location") or {}).get("source", {}).get("display_name", "Academic Venue")

                snippet = f"Published ({pub_year}) in {venue}. Cited by {cited_by} scholarly publications."

                results.append(
                    UnifiedSearchResult(
                        title=f"{title}",
                        url=url,
                        snippet=snippet,
                        source_domain="openalex.org",
                        result_rank=rank,
                        discovery_method="openalex_academic_api",
                        relevance_score=0.90,
                        source_tier=1,
                        publisher=venue,
                        published_date=str(pub_year) if pub_year else None,
                    )
                )

            return results
        except Exception:
            return []
