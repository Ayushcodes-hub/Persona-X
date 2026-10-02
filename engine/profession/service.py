from typing import Iterable, List

from engine.profession.registry import normalize_profession
from engine.profession.router import ProfessionRouter
from engine.profession.schemas import (
    ProfessionAnalysis,
    ProfessionEvidence,
)


class ProfessionAnalysisService:
    def __init__(self):
        self.router = ProfessionRouter()

    def analyze(
        self,
        person_name: str,
        professions: Iterable[str],
        evidence: Iterable[ProfessionEvidence],
    ) -> ProfessionAnalysis:
        normalized_professions = []

        for profession in professions:
            normalized = normalize_profession(profession)

            if normalized not in normalized_professions:
                normalized_professions.append(normalized)

        evidence_list = list(evidence)

        profiles = self.router.build_profiles(
            normalized_professions,
            evidence_list,
        )

        findings = self.router.analyze(
            normalized_professions,
            evidence_list,
        )

        confidence_values = [
            item.confidence
            for item in evidence_list
        ]

        confidence = (
            sum(confidence_values) / len(confidence_values)
            if confidence_values
            else 0.0
        )

        return ProfessionAnalysis(
            person_name=person_name,
            professions=normalized_professions,
            profiles=profiles,
            findings=findings,
            evidence_count=len(evidence_list),
            confidence=round(confidence, 4),
        )