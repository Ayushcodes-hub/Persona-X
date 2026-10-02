from typing import Iterable, List

from engine.profession.base import ProfessionAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
)


class ActorAnalyzer(ProfessionAnalyzer):
    profession = "actor"

    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        findings = []

        supported = {
            "film",
            "films",
            "television",
            "role",
            "roles",
            "award",
            "awards",
            "interview",
            "statement",
            "production",
            "business",
            "endorsement",
            "philanthropy",
        }

        for item in evidence:
            category = item.category.lower()

            if category in supported:
                findings.append(
                    ProfessionFinding(
                        profession="actor",
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