from typing import Iterable, List

from engine.profession.base import ProfessionAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
)


class JournalistAnalyzer(ProfessionAnalyzer):
    profession = "journalist"

    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        findings = []

        supported = {
            "publication",
            "publications",
            "newsroom",
            "reporting",
            "investigation",
            "investigations",
            "interview",
            "commentary",
            "editorial_position",
            "award",
            "awards",
            "public_statement",
        }

        for item in evidence:
            category = item.category.lower()

            if category in supported:
                findings.append(
                    ProfessionFinding(
                        profession="journalist",
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