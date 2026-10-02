from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class IdentityCandidate:
    name: str
    profession: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    match_score: float = 0.0
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)


@dataclass
class IdentityResolution:
    query_name: str
    status: str
    confidence: float
    canonical_name: Optional[str] = None
    candidates: List[IdentityCandidate] = field(default_factory=list)
    ambiguity_notes: Optional[str] = None
