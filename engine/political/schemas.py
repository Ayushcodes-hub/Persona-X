from dataclasses import dataclass, field
from typing import List, Optional


POLITICAL_EVIDENCE_TYPES = {
    "self_identification",
    "party_affiliation",
    "policy_statement",
    "political_action",
    "legislative_record",
    "campaign_activity",
    "political_office",
    "endorsement",
    "public_advocacy",
    "political_interview",
    "institutional_record",
    "secondary_analysis",
}


POLITICAL_POSITION_TYPES = {
    "support",
    "oppose",
    "favor",
    "against",
    "mixed",
    "unclear",
    "not_stated",
}


@dataclass
class PoliticalEvidence:
    evidence_type: str
    text: str
    topic: Optional[str] = None
    issue: Optional[str] = None
    position: Optional[str] = None
    evidence_id: Optional[int] = None
    source_id: Optional[int] = None
    statement_id: Optional[int] = None
    event_date: Optional[str] = None
    source_tier: Optional[int] = None
    verification_status: str = "unverified"
    attribution_status: str = "unknown"
    confidence: float = 0.0


@dataclass
class PoliticalPosition:
    dimension: str
    issue: str
    position: str
    evidence_ids: List[int] = field(default_factory=list)
    source_ids: List[int] = field(default_factory=list)
    dates: List[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence_status: str = "documented"


@dataclass
class PoliticalDimension:
    name: str
    positions: List[PoliticalPosition] = field(default_factory=list)
    evidence_count: int = 0
    confidence: float = 0.0


@dataclass
class PoliticalConflict:
    dimension: str
    issue: str
    earlier_position: str
    later_position: str
    earlier_date: Optional[str] = None
    later_date: Optional[str] = None
    evidence_ids: List[int] = field(default_factory=list)
    confidence: float = 0.0
    classification: str = "potential_inconsistency"


@dataclass
class PoliticalSufficiency:
    sufficient: bool
    evidence_count: int
    qualifying_evidence_count: int
    dimensions_covered: int
    confidence: float
    reason: str


@dataclass
class PoliticalSpectrum:
    """
    Evidence-grounded left-to-right political spectrum assessment.
    Scores range from -1.0 (Left) to +1.0 (Right).
    """
    applicable: bool
    spectrum_score: Optional[float] = None
    spectrum_label: str = "Insufficient Public Political Record"
    economic_axis: Optional[float] = None
    social_axis: Optional[float] = None
    governance_axis: Optional[float] = None
    foreign_policy_axis: Optional[float] = None
    rationale: str = ""
    confidence: float = 0.0
    key_indicators: List[str] = field(default_factory=list)


@dataclass
class PoliticalAnalysis:
    person_name: str
    applicable: bool
    sufficiency: PoliticalSufficiency
    dimensions: List[PoliticalDimension] = field(default_factory=list)
    conflicts: List[PoliticalConflict] = field(default_factory=list)
    political_activity: List[PoliticalEvidence] = field(default_factory=list)
    spectrum: Optional[PoliticalSpectrum] = None
    evidence_count: int = 0
    confidence: float = 0.0
    limitations: List[str] = field(default_factory=list)