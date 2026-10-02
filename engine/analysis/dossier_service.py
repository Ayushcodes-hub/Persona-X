from typing import Iterable, Optional

from engine.analysis.dossier_narrator import DossierNarrator
from engine.analysis.dossier_schemas import (
    DossierFinding,
    DossierSection,
    DossierSynthesis,
)
from engine.analysis.dossier_synthesizer import DossierSynthesizer


class DossierService:

    def __init__(
        self,
        synthesizer: Optional[DossierSynthesizer] = None,
        narrator: Optional[DossierNarrator] = None,
    ) -> None:
        self.synthesizer = synthesizer or DossierSynthesizer()
        self.narrator = narrator or DossierNarrator()

    def build(
        self,
        person_name: str,
        canonical_name: Optional[str] = None,
        professions: Optional[Iterable[str]] = None,
        sections: Optional[Iterable[DossierSection]] = None,
        findings: Optional[Iterable[DossierFinding]] = None,
        source_count: int = 0,
        evidence_count: int = 0,
        political_analysis_included: bool = False,
        limitations: Optional[Iterable[str]] = None,
    ) -> DossierSynthesis:

        return self.synthesizer.synthesize(
            person_name=person_name,
            canonical_name=canonical_name,
            professions=professions,
            sections=sections,
            findings=findings,
            source_count=source_count,
            evidence_count=evidence_count,
            political_analysis_included=political_analysis_included,
            limitations=limitations,
        )

    def render(
        self,
        dossier: DossierSynthesis,
    ) -> str:
        return self.narrator.render(dossier)