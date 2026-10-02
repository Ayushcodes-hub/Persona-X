from typing import Iterable, List

from engine.profession.base import ProfessionAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
)


class GenericAnalyzer(ProfessionAnalyzer):
    profession = "generic"

    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        findings = []

        for item in evidence:
            findings.append(
                ProfessionFinding(
                    profession="generic",
                    category=item.category,
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