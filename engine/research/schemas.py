from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: Optional[str] = None
    source_domain: Optional[str] = None
    result_rank: Optional[int] = None
    discovery_method: str = "browser_search"
    relevance_score: Optional[float] = None
    published_at: Optional[str] = None


@dataclass
class ResearchResponse:
    query: str
    results: List[SearchResult] = field(default_factory=list)
    search_status: str = "completed"
    error: Optional[str] = None
