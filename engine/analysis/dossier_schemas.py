from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DossierSection:
    key: str
    title: str
    content: str
    evidence_ids: List[int] = field(default_factory=list)
    source_ids: List[int] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class DossierFinding:
    finding_type: str
    title: str
    description: str
    evidence_ids: List[int] = field(default_factory=list)
    source_ids: List[int] = field(default_factory=list)
    confidence: Optional[float] = None
    status: str = "supported"


@dataclass
class DossierSynthesis:
    person_name: str
    canonical_name: Optional[str]
    profession: List[str] = field(default_factory=list)

    executive_summary: str = ""

    sections: List[DossierSection] = field(default_factory=list)
    findings: List[DossierFinding] = field(default_factory=list)

    source_count: int = 0
    evidence_count: int = 0

    completeness_score: float = 0.0
    evidence_coverage_score: float = 0.0
    confidence: Optional[float] = None

    political_analysis_included: bool = False
    limitations: List[str] = field(default_factory=list)