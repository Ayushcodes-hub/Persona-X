from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TopicMention:
    """
    A structured topic identified in evidence, a statement, or a claim.

    A topic describes what the material concerns.
    It does not establish a person's position.
    """

    topic: str
    subject: Optional[str] = None
    subtopic: Optional[str] = None
    context: Optional[str] = None
    source_text: Optional[str] = None
    confidence: float = 0.0
    extraction_method: str = "deterministic"
    status: str = "extracted"


@dataclass
class ViewMention:
    """
    A structured representation of a documented view or position.

    A view requires stronger evidence than merely mentioning a topic.
    """

    topic: str
    subject: Optional[str] = None
    position: Optional[str] = None
    position_type: Optional[str] = None
    context: Optional[str] = None
    supporting_text: Optional[str] = None
    confidence: float = 0.0
    attribution_status: str = "unverified"
    extraction_method: str = "deterministic"
    status: str = "extracted"


@dataclass
class TopicExtractionResult:
    """
    Complete extraction result for one research item.
    """

    topics: List[TopicMention] = field(default_factory=list)
    views: List[ViewMention] = field(default_factory=list)

    @property
    def topic_count(self) -> int:
        return len(self.topics)

    @property
    def view_count(self) -> int:
        return len(self.views)