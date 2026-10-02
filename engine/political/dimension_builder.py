from collections import defaultdict
from typing import Iterable, List

from engine.political.schemas import (
    PoliticalDimension,
    PoliticalPosition,
)


class PoliticalDimensionBuilder:
    def build(
        self,
        positions: Iterable[PoliticalPosition],
    ) -> List[PoliticalDimension]:
        grouped = defaultdict(list)

        for position in positions:
            grouped[position.dimension].append(position)

        dimensions = []

        for name, items in grouped.items():
            confidence = (
                sum(item.confidence for item in items)
                / len(items)
                if items
                else 0.0
            )

            evidence_count = sum(
                len(item.evidence_ids)
                for item in items
            )

            dimensions.append(
                PoliticalDimension(
                    name=name,
                    positions=list(items),
                    evidence_count=evidence_count,
                    confidence=round(confidence, 4),
                )
            )

        return dimensions