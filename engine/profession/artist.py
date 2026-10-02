from typing import Iterable, List

from engine.profession.base import ProfessionAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
)


class ArtistAnalyzer(ProfessionAnalyzer):
    profession = "artist"

    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        findings = []

        supported = {
            "work",
            "works",
            "exhibition",
            "exhibitions",
            "collection",
            "collections",
            "award",
            "awards",
            "interview",
            "theme",
            "themes",
            "public_statement",
            "commission",
            "commissions",
            "public_activity",
        }

        for item in evidence:
            category = item.category.lower()

            if category in supported:
                findings.append(
                    ProfessionFinding(
                        profession="artist",
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