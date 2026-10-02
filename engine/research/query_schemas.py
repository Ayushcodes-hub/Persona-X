from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryVariant:
    query_text: str
    variant_type: str
    source_focus: str = "general"
    temporal_scope: Optional[str] = None
    priority: int = 5
    source_target: Optional[str] = None
    disambiguation_context: Optional[str] = None


@dataclass
class QueryBundle:
    task_id: str
    variants: list[QueryVariant]

    @property
    def query_count(self) -> int:
        return len(self.variants)