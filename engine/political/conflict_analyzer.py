from typing import Iterable, List, Tuple

from engine.political.schemas import (
    PoliticalConflict,
    PoliticalEvidence,
)


OPPOSING_POSITIONS = {
    ("support", "oppose"),
    ("support", "against"),
    ("favor", "oppose"),
    ("favor", "against"),
    ("oppose", "support"),
    ("oppose", "favor"),
    ("against", "support"),
    ("against", "favor"),
}


class PoliticalConflictAnalyzer:
    def analyze(
        self,
        evidence: Iterable[PoliticalEvidence],
    ) -> List[PoliticalConflict]:
        items = [
            item
            for item in evidence
            if item.topic
            and item.issue
            and item.position
        ]

        conflicts = []

        for index, earlier in enumerate(items):
            for later in items[index + 1:]:
                if (
                    earlier.topic != later.topic
                    or earlier.issue != later.issue
                ):
                    continue

                pair: Tuple[str, str] = (
                    earlier.position.lower(),
                    later.position.lower(),
                )

                if pair not in OPPOSING_POSITIONS:
                    continue

                if not earlier.event_date or not later.event_date:
                    continue

                if earlier.event_date > later.event_date:
                    earlier, later = later, earlier

                evidence_ids = []

                if earlier.evidence_id is not None:
                    evidence_ids.append(earlier.evidence_id)

                if later.evidence_id is not None:
                    evidence_ids.append(later.evidence_id)

                confidence = (
                    earlier.confidence + later.confidence
                ) / 2

                conflicts.append(
                    PoliticalConflict(
                        dimension=earlier.topic,
                        issue=earlier.issue,
                        earlier_position=earlier.position,
                        later_position=later.position,
                        earlier_date=earlier.event_date,
                        later_date=later.event_date,
                        evidence_ids=evidence_ids,
                        confidence=round(confidence, 4),
                        classification="potential_inconsistency",
                    )
                )

        return conflicts