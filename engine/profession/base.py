from abc import ABC, abstractmethod
from typing import Iterable, List

from engine.profession.registry import get_capabilities, normalize_profession
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
    ProfessionProfile,
)


class ProfessionAnalyzer(ABC):
    profession = "generic"

    def build_profile(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> ProfessionProfile:
        evidence_list = list(evidence)

        return ProfessionProfile(
            profession=normalize_profession(self.profession),
            title=self.profession.title(),
            capabilities=get_capabilities(self.profession),
            evidence=evidence_list,
            confidence=self._calculate_confidence(evidence_list),
        )

    def _calculate_confidence(
        self,
        evidence: List[ProfessionEvidence],
    ) -> float:
        if not evidence:
            return 0.0

        confidence = sum(
            max(0.0, min(1.0, item.confidence))
            for item in evidence
        ) / len(evidence)

        return round(confidence, 4)

    @abstractmethod
    def analyze(
        self,
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        raise NotImplementedError