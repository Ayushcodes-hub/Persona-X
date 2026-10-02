from typing import List
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from engine.research.search.base import BaseSearchAdapter, SearchQuerySpec, UnifiedSearchResult
from backend.app.utils.security import is_safe_url


class DuckDuckGoSearchAdapter(BaseSearchAdapter):
    """
    Search DuckDuckGo public web search with snippet extraction.
    """

    SEARCH_URL = "https://html.duckduckgo.com/html/"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    @property
    def adapter_name(self) -> str:
        return "duckduckgo_web"

    def _extract_real_url(self, raw_url: str) -> str:
        # DDG html links often wrap target URLs: /l/?kh=-1&uddg=https%3A%2F%2F...
        if "/l/?" in raw_url and "uddg=" in raw_url:
            parsed = urlparse(raw_url)
            qs = parse_qs(parsed.query)
            uddg = qs.get("uddg")
            if uddg:
                return unquote(uddg[0])
        return raw_url

    def search(self, spec: SearchQuerySpec) -> List[UnifiedSearchResult]:
        query = spec.query.strip()
        if not query:
            return []

        data = {"q": query}
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,text/plain",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(self.SEARCH_URL, data=data, headers=headers)
                if res.status_code != 200:
                    return []
                html = res.text

            soup = BeautifulSoup(html, "lxml")
            results = []
            elements = soup.select(".result")

            for rank, elem in enumerate(elements[:spec.max_results], start=1):
                title_elem = elem.select_one(".result__title a")
                snippet_elem = elem.select_one(".result__snippet")

                if not title_elem:
                    continue

                raw_href = title_elem.get("href", "")
                real_url = self._extract_real_url(raw_href)

                if not is_safe_url(real_url):
                    continue

                title = title_elem.get_text(" ", strip=True)
                snippet = snippet_elem.get_text(" ", strip=True) if snippet_elem else ""

                domain = urlparse(real_url).hostname

                results.append(
                    UnifiedSearchResult(
                        title=title,
                        url=real_url,
                        snippet=snippet or f"Web result for {query}.",
                        source_domain=domain,
                        result_rank=rank,
                        discovery_method="duckduckgo_web",
                        relevance_score=0.85,
                        source_tier=2,
                    )
                )

            return results
        except Exception:
            return []
