from typing import Iterable, List

from engine.profession.base import ProfessionAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
)


class EntrepreneurAnalyzer(ProfessionAnalyzer):
    profession = "entrepreneur"

    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        findings = []

        supported = {
            "company",
            "companies",
            "founding",
            "leadership",
            "funding",
            "product",
            "products",
            "investment",
            "investments",
            "business_strategy",
            "business_statement",
            "public_policy",
            "initiative",
        }

        for item in evidence:
            category = item.category.lower()

            if category in supported:
                findings.append(
                    ProfessionFinding(
                        profession="entrepreneur",
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