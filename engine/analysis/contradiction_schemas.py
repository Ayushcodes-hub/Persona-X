from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ClaimObservation:
    """
    Evidence-backed representation of a claim for comparison.

    This object deliberately preserves the original wording and evidence
    identity. Normalized fields are used only for comparison.
    """

    claim_text: str
    topic: Optional[str] = None
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object_value: Optional[str] = None

    observation_date: Optional[str] = None
    context: Optional[str] = None

    position: Optional[str] = None
    polarity: Optional[str] = None

    evidence_id: Optional[int] = None
    source_id: Optional[int] = None

    verification_status: str = "unverified"
    confidence: float = 0.0


@dataclass
class ClaimComparison:
    """
    Comparison between two documented claims.

    'potential_inconsistency' means the evidence contains opposing
    propositions that require contextual interpretation. It does not
    establish motive, dishonesty, hypocrisy, or wrongdoing.
    """

    status: str

    reason: str

    confidence: float

    topic_match: bool
    subject_match: bool
    proposition_match: bool
    polarity_conflict: bool

    earlier_claim: Optional[ClaimObservation] = None
    later_claim: Optional[ClaimObservation] = None


@dataclass
class ContradictionAnalysis:
    """
    Complete contradiction analysis for a collection of claims.
    """

    comparisons: List[ClaimComparison]

    @property
    def comparison_count(self) -> int:
        return len(self.comparisons)

    @property
    def potential_inconsistency_count(self) -> int:
        return sum(
            comparison.status == "potential_inconsistency"
            for comparison in self.comparisons
        )

    @property
    def compatible_count(self) -> int:
        return sum(
            comparison.status == "compatible"
            for comparison in self.comparisons
        )

    @property
    def insufficient_evidence_count(self) -> int:
        return sum(
            comparison.status == "insufficient_evidence"
            for comparison in self.comparisons
        )