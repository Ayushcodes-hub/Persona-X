from typing import Dict, Iterable, List

from engine.profession.academic import AcademicAnalyzer
from engine.profession.actor import ActorAnalyzer
from engine.profession.athlete import AthleteAnalyzer
from engine.profession.artist import ArtistAnalyzer
from engine.profession.author import AuthorAnalyzer
from engine.profession.base import ProfessionAnalyzer
from engine.profession.entrepreneur import EntrepreneurAnalyzer
from engine.profession.generic import GenericAnalyzer
from engine.profession.journalist import JournalistAnalyzer
from engine.profession.politician import PoliticianAnalyzer
from engine.profession.scientist import ScientistAnalyzer
from engine.profession.schemas import (
    ProfessionEvidence,
    ProfessionFinding,
    ProfessionProfile,
)
from engine.profession.registry import normalize_profession


ANALYZER_REGISTRY: Dict[str, ProfessionAnalyzer] = {
    "athlete": AthleteAnalyzer(),
    "actor": ActorAnalyzer(),
    "scientist": ScientistAnalyzer(),
    "entrepreneur": EntrepreneurAnalyzer(),
    "politician": PoliticianAnalyzer(),
    "journalist": JournalistAnalyzer(),
    "author": AuthorAnalyzer(),
    "academic": AcademicAnalyzer(),
    "artist": ArtistAnalyzer(),
    "generic": GenericAnalyzer(),
}


class ProfessionRouter:
    def __init__(self):
        self.registry = ANALYZER_REGISTRY

    def get_analyzer(self, profession: str) -> ProfessionAnalyzer:
        normalized = normalize_profession(profession)

        return self.registry.get(
            normalized,
            self.registry["generic"],
        )

    def build_profiles(
        self,
        professions: Iterable[str],
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionProfile]:
        evidence_list = list(evidence)
        profiles = []

        for profession in professions:
            analyzer = self.get_analyzer(profession)

            profiles.append(
                analyzer.build_profile(evidence_list)
            )

        return profiles

    def analyze(
        self,
        professions: Iterable[str],
        evidence: Iterable[ProfessionEvidence],
    ) -> List[ProfessionFinding]:
        evidence_list = list(evidence)
        findings: List[ProfessionFinding] = []

        for profession in professions:
            analyzer = self.get_analyzer(profession)

            findings.extend(
                analyzer.analyze(evidence_list)
            )

        return findings