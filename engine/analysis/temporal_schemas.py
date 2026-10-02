from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TemporalObservation:
    """
    A dated, evidence-backed observation about a person's topic or view.

    The date belongs to the observation itself. A missing date means the
    observation cannot safely participate in chronological evolution analysis.
    """

    topic: str
    observation_date: Optional[str] = None
    position: Optional[str] = None
    position_type: Optional[str] = None
    source_text: Optional[str] = None
    source_id: Optional[int] = None
    evidence_id: Optional[int] = None
    context: Optional[str] = None
    attribution_status: str = "unverified"
    confidence: float = 0.0


@dataclass
class TemporalChange:
    """
    A documented comparison between two observations.

    This object describes evidence-supported temporal difference.
    It does not infer motive or intent.
    """

    topic: str
    earlier_date: str
    later_date: str
    earlier_position: Optional[str]
    later_position: Optional[str]
    earlier_position_type: Optional[str] = None
    later_position_type: Optional[str] = None
    change_type: str = "undetermined"
    explanation: Optional[str] = None
    earlier_evidence_id: Optional[int] = None
    later_evidence_id: Optional[int] = None
    confidence: float = 0.0


@dataclass
class TemporalTopicAnalysis:
    """
    Temporal analysis for one topic.
    """

    topic: str
    observations: List[TemporalObservation] = field(
        default_factory=list
    )
    changes: List[TemporalChange] = field(
        default_factory=list
    )
    status: str = "insufficient_evidence"

    @property
    def observation_count(self) -> int:
        return len(self.observations)

    @property
    def change_count(self) -> int:
        return len(self.changes)


@dataclass
class TemporalEvolutionResult:
    """
    Complete temporal evolution result across all supplied topics.
    """

    analyses: List[TemporalTopicAnalysis] = field(
        default_factory=list
    )

    @property
    def topic_count(self) -> int:
        return len(self.analyses)

    @property
    def change_count(self) -> int:
        return sum(
            analysis.change_count
            for analysis in self.analyses
        )