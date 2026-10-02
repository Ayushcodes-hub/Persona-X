import re
from typing import List
from urllib.parse import quote

import httpx

from engine.research.search.base import BaseSearchAdapter, SearchQuerySpec, UnifiedSearchResult
from backend.app.utils.security import is_safe_url


class WikipediaSearchAdapter(BaseSearchAdapter):
    """
    Search Wikipedia API for biographical, institutional, and historical grounding.
    """

    API_URL = "https://en.wikipedia.org/w/api.php"
    USER_AGENT = "PersonaXBot/1.0 (https://github.com/persona-x; persona-x@example.com) httpx/0.28"

    @property
    def adapter_name(self) -> str:
        return "wikipedia"

    def search(self, spec: SearchQuerySpec) -> List[UnifiedSearchResult]:
        query = spec.query.strip()
        if not query:
            return []

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": min(spec.max_results, 10),
            "utf8": 1,
        }

        try:
            with httpx.Client(timeout=10.0, headers={"User-Agent": self.USER_AGENT}) as client:
                res = client.get(self.API_URL, params=params)
                if res.status_code != 200:
                    return []
                data = res.json()

            items = data.get("query", {}).get("search", [])
            results = []
            for rank, item in enumerate(items, start=1):
                title = item.get("title", "")
                snippet_raw = item.get("snippet", "")
                # Clean html tags from snippet
                snippet = re.sub(r"<[^>]+>", "", snippet_raw).strip()
                url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"

                if not is_safe_url(url):
                    continue

                results.append(
                    UnifiedSearchResult(
                        title=f"{title} — Wikipedia",
                        url=url,
                        snippet=snippet or f"Wikipedia encyclopedic reference for {title}.",
                        source_domain="en.wikipedia.org",
                        result_rank=rank,
                        discovery_method="wikipedia_api",
                        relevance_score=0.92,
                        source_tier=1,
                        publisher="Wikipedia, The Free Encyclopedia",
                    )
                )

            return results
        except Exception:
            return []
