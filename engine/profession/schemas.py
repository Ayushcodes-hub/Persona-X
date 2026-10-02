from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProfessionEvidence:
    category: str
    value: str
    evidence_id: Optional[int] = None
    source_id: Optional[int] = None
    confidence: float = 0.0


@dataclass
class ProfessionProfile:
    profession: str
    title: str
    capabilities: List[str] = field(default_factory=list)
    evidence: List[ProfessionEvidence] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ProfessionFinding:
    profession: str
    category: str
    finding: str
    evidence_ids: List[int] = field(default_factory=list)
    source_ids: List[int] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ProfessionAnalysis:
    person_name: str
    professions: List[str]
    profiles: List[ProfessionProfile] = field(default_factory=list)
    findings: List[ProfessionFinding] = field(default_factory=list)
    evidence_count: int = 0
    confidence: float = 0.0