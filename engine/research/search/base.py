from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchQuerySpec:
    query: str
    max_results: int = 10
    profession_context: Optional[str] = None
    topic: Optional[str] = None
    language: str = "en"


@dataclass
class UnifiedSearchResult:
    title: str
    url: str
    snippet: str
    source_domain: Optional[str] = None
    result_rank: int = 1
    discovery_method: str = "web"
    relevance_score: float = 0.5
    source_tier: int = 2
    publisher: Optional[str] = None
    published_date: Optional[str] = None


class BaseSearchAdapter(ABC):
    @property
    @abstractmethod
    def adapter_name(self) -> str:
        pass

    @abstractmethod
    def search(self, spec: SearchQuerySpec) -> List[UnifiedSearchResult]:
        pass
