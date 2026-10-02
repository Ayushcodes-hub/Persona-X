from typing import List, Optional

from engine.analysis.contradiction_analyzer import (
    ContradictionAnalyzer,
)
from engine.analysis.contradiction_schemas import (
    ClaimObservation,
    ClaimComparison,
    ContradictionAnalysis,
)


class ContradictionAnalysisService:
    """
    Public service for contradiction / potential inconsistency analysis.
    """

    def __init__(
        self,
        analyzer: Optional[
            ContradictionAnalyzer
        ] = None,
    ):
        self.analyzer = (
            analyzer or ContradictionAnalyzer()
        )

    def compare(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> ClaimComparison:
        return self.analyzer.compare(
            first,
            second,
        )

    def analyze(
        self,
        claims: List[ClaimObservation],
    ) -> ContradictionAnalysis:
        return self.analyzer.analyze(
            claims
        )