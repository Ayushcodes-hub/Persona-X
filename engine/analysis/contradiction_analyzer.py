from datetime import date
from typing import List, Optional, Tuple

from engine.analysis.contradiction_classifier import (
    ContradictionClassifier,
)
from engine.analysis.contradiction_schemas import (
    ClaimComparison,
    ClaimObservation,
    ContradictionAnalysis,
)


class ContradictionAnalyzer:
    """
    Performs pairwise comparison of evidence-backed claims.

    The analyzer deliberately does not infer intent, motive, deception,
    hypocrisy, or wrongdoing.
    """

    def __init__(
        self,
        classifier: Optional[
            ContradictionClassifier
        ] = None,
    ):
        self.classifier = (
            classifier or ContradictionClassifier()
        )

    @staticmethod
    def _date_key(
        value: Optional[str],
    ) -> Tuple[int, str]:
        if not value:
            return (
                1,
                "",
            )

        try:
            parsed = date.fromisoformat(value)
            return (
                0,
                parsed.isoformat(),
            )
        except ValueError:
            return (
                1,
                value,
            )

    def order_claims(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> Tuple[
        ClaimObservation,
        ClaimObservation,
    ]:
        first_key = self._date_key(
            first.observation_date
        )

        second_key = self._date_key(
            second.observation_date
        )

        if first_key <= second_key:
            return first, second

        return second, first

    def compare(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> ClaimComparison:
        earlier, later = self.order_claims(
            first,
            second,
        )

        (
            status,
            confidence,
            reason,
            topic_match,
            subject_match,
            proposition_match,
            polarity_conflict,
        ) = self.classifier.classify(
            earlier,
            later,
        )

        return ClaimComparison(
            status=status,
            reason=reason,
            confidence=confidence,
            topic_match=topic_match,
            subject_match=subject_match,
            proposition_match=proposition_match,
            polarity_conflict=polarity_conflict,
            earlier_claim=earlier,
            later_claim=later,
        )

    def analyze(
        self,
        claims: List[ClaimObservation],
    ) -> ContradictionAnalysis:
        comparisons: List[
            ClaimComparison
        ] = []

        for index, first in enumerate(claims):
            for second in claims[index + 1:]:
                comparisons.append(
                    self.compare(
                        first,
                        second,
                    )
                )

        return ContradictionAnalysis(
            comparisons=comparisons
        )