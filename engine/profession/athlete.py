from typing import Iterable, List

from engine.profession.base import ProfessionAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
)


class AthleteAnalyzer(ProfessionAnalyzer):
    profession = "athlete"

    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        findings = []

        for item in evidence:
            category = item.category.lower()

            if category in {
                "team",
                "teams",
                "competition",
                "competitions",
                "performance",
                "performances",
                "record",
                "records",
                "award",
                "awards",
                "interview",
                "statement",
                "endorsement",
                "philanthropy",
            }:
                findings.append(
                    ProfessionFinding(
                        profession="athlete",
                        category=category,
                        finding=item.value,
                        evidence_ids=(
                            [item.evidence_id]
                            if item.evidence_id is not None
                            else []
                        ),
                        source_ids=(
                            [item.source_id]
                            if item.source_id is not None
                            else []
                        ),
                        confidence=item.confidence,
                    )
                )

        return findings