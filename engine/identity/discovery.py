import re
from typing import List, Optional
from urllib.parse import quote

import httpx

from engine.identity.schemas import IdentityCandidate
from engine.profession.registry import normalize_profession
from backend.app.utils.security import sanitize_search_query


class IdentityDiscoveryService:
    """
    Universal public-person identity discovery engine.
    Queries Wikidata and Wikipedia to discover verified canonical public person candidates.
    """

    WIKIDATA_SEARCH_URL = "https://www.wikidata.org/w/api.php"
    WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
    USER_AGENT = "PersonaXBot/1.0 (https://github.com/persona-x; persona-x@example.com) httpx/0.28"

    def _infer_profession_from_text(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        keywords = {
            "cricketer": "athlete",
            "cricket": "athlete",
            "footballer": "athlete",
            "player": "athlete",
            "athlete": "athlete",
            "swimmer": "athlete",
            "actor": "actor",
            "actress": "actor",
            "filmmaker": "actor",
            "director": "actor",
            "scientist": "scientist",
            "physicist": "scientist",
            "chemist": "scientist",
            "biologist": "scientist",
            "researcher": "scientist",
            "entrepreneur": "entrepreneur",
            "businessman": "entrepreneur",
            "businesswoman": "entrepreneur",
            "founder": "entrepreneur",
            "ceo": "entrepreneur",
            "politician": "politician",
            "prime minister": "politician",
            "president": "politician",
            "minister": "politician",
            "senator": "politician",
            "journalist": "journalist",
            "reporter": "journalist",
            "author": "author",
            "writer": "author",
            "novelist": "author",
            "professor": "academic",
            "academic": "academic",
            "scholar": "academic",
            "artist": "artist",
            "painter": "artist",
            "musician": "artist",
            "singer": "artist",
        }
        for kw, prof in keywords.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                return normalize_profession(prof)
        return None

    def _infer_nationality_from_text(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        countries = {
            "indian": "India",
            "american": "United States",
            "british": "United Kingdom",
            "english": "United Kingdom",
            "french": "France",
            "german": "Germany",
            "australian": "Australia",
            "canadian": "Canada",
            "japanese": "Japan",
            "chinese": "China",
            "brazilian": "Brazil",
            "south african": "South Africa",
            "russian": "Russia",
            "polish": "Poland",
        }
        for dem, nation in countries.items():
            if re.search(r"\b" + re.escape(dem) + r"\b", text_lower):
                return nation
        return None

    def discover_candidates(self, person_name: str, max_candidates: int = 5) -> List[IdentityCandidate]:
        clean_name = sanitize_search_query(person_name)
        if not clean_name:
            return []

        candidates: List[IdentityCandidate] = []
        seen_names = set()

        # 1. Query Wikidata for structured person entities
        try:
            params = {
                "action": "wbsearchentities",
                "search": clean_name,
                "language": "en",
                "format": "json",
                "limit": max_candidates,
                "type": "item",
            }
            with httpx.Client(timeout=8.0, headers={"User-Agent": self.USER_AGENT}) as client:
                res = client.get(self.WIKIDATA_SEARCH_URL, params=params)
                if res.status_code == 200:
                    data = res.json()
                    for item in data.get("search", []):
                        label = item.get("label", "").strip()
                        description = item.get("description", "")
                        url = item.get("concepturi") or f"https://www.wikidata.org/wiki/{item.get('id')}"

                        if not label or label.lower() in seen_names:
                            continue

                        profession = self._infer_profession_from_text(description)
                        nationality = self._infer_nationality_from_text(description)

                        # Extract birth year if present (e.g. "born 1993")
                        birth_year = None
                        year_match = re.search(r"\b(?:born\s+)?(1[89]\d\d|20[0-2]\d)\b", description)
                        if year_match:
                            birth_year = year_match.group(1)

                        # Match score heuristic
                        name_match = 0.85 if label.lower() == clean_name.lower() else 0.65
                        confidence = name_match + (0.1 if profession else 0.0)

                        candidates.append(
                            IdentityCandidate(
                                name=label,
                                profession=profession,
                                nationality=nationality,
                                birth_date=birth_year,
                                source_url=url,
                                source_title=f"{label} ({item.get('id')}) on Wikidata",
                                match_score=min(confidence, 1.0),
                                confidence=min(confidence, 1.0),
                                reasons=[f"Wikidata entity match: {description}"] if description else ["Wikidata entity match"],
                            )
                        )
                        seen_names.add(label.lower())
        except Exception:
            pass

        # 2. Query Wikipedia if candidates are scarce
        if len(candidates) < 2:
            try:
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": clean_name,
                    "format": "json",
                    "srlimit": 3,
                }
                with httpx.Client(timeout=8.0, headers={"User-Agent": self.USER_AGENT}) as client:
                    res = client.get(self.WIKIPEDIA_API_URL, params=params)
                    if res.status_code == 200:
                        data = res.json()
                        for item in data.get("query", {}).get("search", []):
                            title = item.get("title", "").strip()
                            snippet = re.sub(r"<[^>]+>", "", item.get("snippet", "")).strip()
                            url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"

                            if not title or title.lower() in seen_names:
                                continue

                            profession = self._infer_profession_from_text(snippet)
                            nationality = self._infer_nationality_from_text(snippet)

                            candidates.append(
                                IdentityCandidate(
                                    name=title,
                                    profession=profession,
                                    nationality=nationality,
                                    source_url=url,
                                    source_title=f"{title} on Wikipedia",
                                    match_score=0.75 if title.lower() == clean_name.lower() else 0.55,
                                    confidence=0.75,
                                    reasons=["Wikipedia biographical article match"],
                                )
                            )
                            seen_names.add(title.lower())
            except Exception:
                pass

        # Fallback if no external candidate was returned: create an unverified candidate with the query name
        if not candidates:
            candidates.append(
                IdentityCandidate(
                    name=clean_name,
                    match_score=0.70,
                    confidence=0.50,
                    reasons=["Exact query string match (no external candidates returned)"],
                )
            )

        return candidates[:max_candidates]


identity_discovery = IdentityDiscoveryService()
