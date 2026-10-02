from dataclasses import dataclass, field
from typing import Any, List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


@dataclass
class ExtractedCitation:
    title: str
    url: str
    content: Optional[str] = None
    source_domain: Optional[str] = None
    result_rank: Optional[int] = None
    tool_type: Optional[str] = None
    discovery_methods: List[str] = field(default_factory=list)


class CitationExtractor:
    TRACKING_PARAMETERS = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "fbclid",
    }

    def extract_url(self, value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None

        value = value.strip()

        if value.startswith("[") and "](" in value and value.endswith(")"):
            value = value.split("](", 1)[1][:-1]

        if value.startswith(("http://", "https://")):
            return value

        return None

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url.strip())

        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path or "/"

        if path != "/":
            path = path.rstrip("/")

        query_pairs = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key.lower() not in self.TRACKING_PARAMETERS
        ]

        query = urlencode(query_pairs)

        return urlunparse(
            (
                scheme,
                netloc,
                path,
                "",
                query,
                "",
            )
        )

    def _get_value(self, item: Any, key: str, default=None):
        if isinstance(item, dict):
            return item.get(key, default)

        return getattr(item, key, default)

    def extract(self, message: Any) -> List[ExtractedCitation]:
        citations: List[ExtractedCitation] = []
        by_url = {}

        executed_tools = getattr(message, "executed_tools", None) or []

        for tool in executed_tools:
            tool_type = getattr(tool, "type", None)
            search_results = getattr(tool, "search_results", None)

            if not search_results:
                continue

            if isinstance(search_results, dict):
                results = search_results.get("results", [])
            else:
                results = getattr(search_results, "results", []) or []

            for index, item in enumerate(results, start=1):
                title = self._get_value(item, "title", "") or ""
                raw_url = self._get_value(item, "url")
                content = self._get_value(item, "content")

                url = self.extract_url(raw_url)

                if not url:
                    continue

                canonical_url = self.normalize_url(url)

                if canonical_url in by_url:
                    existing = by_url[canonical_url]

                    if tool_type and tool_type not in existing.discovery_methods:
                        existing.discovery_methods.append(tool_type)

                    if not existing.content and content:
                        existing.content = content

                    if not existing.title and title:
                        existing.title = title

                    continue

                citation = ExtractedCitation(
                    title=title,
                    url=canonical_url,
                    content=content,
                    source_domain=urlparse(canonical_url).netloc.lower() or None,
                    result_rank=index,
                    tool_type=tool_type,
                    discovery_methods=[tool_type] if tool_type else [],
                )

                citations.append(citation)
                by_url[canonical_url] = citation

        return citations