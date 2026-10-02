from typing import Iterable

from engine.political.evidence_classifier import PoliticalEvidenceClassifier
from engine.political.schemas import (
    PoliticalEvidence,
    PoliticalSufficiency,
)


class PoliticalSufficiencyAnalyzer:
    MIN_QUALIFYING_EVIDENCE = 2
    MIN_CONFIDENCE = 0.60

    def __init__(self):
        self.classifier = PoliticalEvidenceClassifier()

    def analyze(
        self,
        evidence: Iterable[PoliticalEvidence],
    ) -> PoliticalSufficiency:
        items = self.classifier.classify(evidence)

        qualifying = self.classifier.qualifying_evidence(items)

        dimensions = {
            item.topic
            for item in qualifying
            if item.topic
        }

        direct_count = sum(
            1
            for item in qualifying
            if self.classifier.is_direct(item)
        )

        average_confidence = (
            sum(item.confidence for item in qualifying)
            / len(qualifying)
            if qualifying
            else 0.0
        )

        sufficient = (
            len(qualifying) >= self.MIN_QUALIFYING_EVIDENCE
            and average_confidence >= self.MIN_CONFIDENCE
            and (
                direct_count >= 1
                or len(dimensions) >= 2
            )
        )

        if sufficient:
            reason = (
                "Sufficient political evidence exists for structured analysis."
            )
        elif not qualifying:
            reason = (
                "No sufficiently reliable political evidence was identified."
            )
        else:
            reason = (
                "Political evidence exists, but it is insufficient for "
                "a reliable structured political analysis."
            )

        return PoliticalSufficiency(
            sufficient=sufficient,
            evidence_count=len(items),
            qualifying_evidence_count=len(qualifying),
            dimensions_covered=len(dimensions),
            confidence=round(average_confidence, 4),
            reason=reason,
        )