from collections import defaultdict
from typing import Iterable, List

from engine.political.schemas import (
    PoliticalEvidence,
    PoliticalPosition,
)


VALID_POSITIONS = {
    "support",
    "oppose",
    "favor",
    "against",
    "mixed",
    "unclear",
    "not_stated",
}


class PoliticalPositionAnalyzer:
    def analyze(
        self,
        evidence: Iterable[PoliticalEvidence],
    ) -> List[PoliticalPosition]:
        grouped = defaultdict(list)

        for item in evidence:
            if not item.topic or not item.issue:
                continue

            position = (
                item.position.lower()
                if item.position
                else "not_stated"
            )

            if position not in VALID_POSITIONS:
                position = "unclear"

            if position in {"not_stated", "unclear"}:
                continue

            grouped[
                (item.topic, item.issue, position)
            ].append(item)

        positions = []

        for (dimension, issue, position), items in grouped.items():
            evidence_ids = [
                item.evidence_id
                for item in items
                if item.evidence_id is not None
            ]

            source_ids = [
                item.source_id
                for item in items
                if item.source_id is not None
            ]

            dates = [
                item.event_date
                for item in items
                if item.event_date
            ]

            confidence = (
                sum(item.confidence for item in items)
                / len(items)
            )

            positions.append(
                PoliticalPosition(
                    dimension=dimension,
                    issue=issue,
                    position=position,
                    evidence_ids=evidence_ids,
                    source_ids=source_ids,
                    dates=dates,
                    confidence=round(confidence, 4),
                )
            )

        return positions