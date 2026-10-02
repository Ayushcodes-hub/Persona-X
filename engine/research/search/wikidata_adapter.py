from typing import List

import httpx

from engine.research.search.base import BaseSearchAdapter, SearchQuerySpec, UnifiedSearchResult
from backend.app.utils.security import is_safe_url


class WikidataSearchAdapter(BaseSearchAdapter):
    """
    Search Wikidata API for structured entity records and canonical knowledge anchors.
    """

    API_URL = "https://www.wikidata.org/w/api.php"
    USER_AGENT = "PersonaXBot/1.0 (https://github.com/persona-x; persona-x@example.com) httpx/0.28"

    @property
    def adapter_name(self) -> str:
        return "wikidata"

    def search(self, spec: SearchQuerySpec) -> List[UnifiedSearchResult]:
        query = spec.query.strip()
        if not query:
            return []

        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": spec.language or "en",
            "format": "json",
            "limit": min(spec.max_results, 8),
            "type": "item",
        }

        try:
            with httpx.Client(timeout=10.0, headers={"User-Agent": self.USER_AGENT}) as client:
                res = client.get(self.API_URL, params=params)
                if res.status_code != 200:
                    return []
                data = res.json()

            items = data.get("search", [])
            results = []
            for rank, item in enumerate(items, start=1):
                label = item.get("label", "")
                description = item.get("description", "")
                entity_id = item.get("id", "")
                url = item.get("concepturi") or f"https://www.wikidata.org/wiki/{entity_id}"

                if not is_safe_url(url):
                    continue

                aliases = item.get("aliases", [])
                alias_text = f" (Aliases: {', '.join(aliases[:3])})" if aliases else ""

                results.append(
                    UnifiedSearchResult(
                        title=f"{label} ({entity_id}) — Wikidata Entity",
                        url=url,
                        snippet=f"{description}{alias_text}".strip() or f"Wikidata canonical entity for {label}.",
                        source_domain="www.wikidata.org",
                        result_rank=rank,
                        discovery_method="wikidata_api",
                        relevance_score=0.95,
                        source_tier=1,
                        publisher="Wikidata Knowledge Base",
                    )
                )

            return results
        except Exception:
            return []
