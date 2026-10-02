from typing import Iterable, List

from engine.political.conflict_analyzer import (
    PoliticalConflictAnalyzer,
)
from engine.political.dimension_builder import (
    PoliticalDimensionBuilder,
)
from engine.political.evidence_classifier import (
    PoliticalEvidenceClassifier,
)
from engine.political.position_analyzer import (
    PoliticalPositionAnalyzer,
)
from engine.political.sufficiency import (
    PoliticalSufficiencyAnalyzer,
)
from engine.political.spectrum_analyzer import (
    PoliticalSpectrumAnalyzer,
)
from engine.political.schemas import (
    PoliticalAnalysis,
    PoliticalEvidence,
)


class PoliticalAnalysisService:
    def __init__(self):
        self.classifier = PoliticalEvidenceClassifier()
        self.sufficiency = PoliticalSufficiencyAnalyzer()
        self.positions = PoliticalPositionAnalyzer()
        self.conflicts = PoliticalConflictAnalyzer()
        self.dimensions = PoliticalDimensionBuilder()
        self.spectrum_analyzer = PoliticalSpectrumAnalyzer()

    def analyze(
        self,
        person_name: str,
        evidence: Iterable[PoliticalEvidence],
    ) -> PoliticalAnalysis:
        items = self.classifier.classify(evidence)

        sufficiency = self.sufficiency.analyze(items)

        if not sufficiency.sufficient:
            spectrum = self.spectrum_analyzer.analyze(
                person_name=person_name,
                sufficiency=sufficiency,
                dimensions=[],
                political_activity=[],
            )
            return PoliticalAnalysis(
                person_name=person_name,
                applicable=False,
                sufficiency=sufficiency,
                dimensions=[],
                conflicts=[],
                political_activity=[],
                spectrum=spectrum,
                evidence_count=len(items),
                confidence=sufficiency.confidence,
                limitations=[
                    "Available political evidence is insufficient "
                    "for a structured political profile.",
                    "No ideological classification was inferred.",
                ],
            )

        positions = self.positions.analyze(items)

        dimensions = self.dimensions.build(positions)

        conflicts = self.conflicts.analyze(items)

        political_activity = [
            item
            for item in items
            if item.evidence_type in {
                "political_action",
                "campaign_activity",
                "political_office",
                "party_affiliation",
                "endorsement",
                "legislative_record",
            }
        ]

        spectrum = self.spectrum_analyzer.analyze(
            person_name=person_name,
            sufficiency=sufficiency,
            dimensions=dimensions,
            political_activity=political_activity,
        )

        limitations = []

        if not positions:
            limitations.append(
                "Political activity was documented, but explicit "
                "issue positions were insufficiently documented."
            )

        if conflicts:
            limitations.append(
                "Some evidence contains opposing documented positions "
                "across time; this is reported as potential inconsistency "
                "without inferring motive."
            )

        return PoliticalAnalysis(
            person_name=person_name,
            applicable=True,
            sufficiency=sufficiency,
            dimensions=dimensions,
            conflicts=conflicts,
            political_activity=political_activity,
            spectrum=spectrum,
            evidence_count=len(items),
            confidence=sufficiency.confidence,
            limitations=limitations,
        )