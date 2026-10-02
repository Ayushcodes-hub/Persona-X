from typing import List, Optional

from engine.analysis.temporal_analyzer import (
    TemporalEvolutionAnalyzer,
)
from engine.analysis.temporal_observation import (
    TemporalObservationBuilder,
)
from engine.analysis.temporal_schemas import (
    TemporalEvolutionResult,
    TemporalObservation,
)
from engine.analysis.topic_schemas import ViewMention


class TemporalEvolutionService:
    """
    Public service for temporal evolution analysis.

    Supports two entry points:

    1. Direct TemporalObservation objects.
    2. ViewMention objects plus explicitly supplied dates.
    """

    def __init__(
        self,
        analyzer: Optional[
            TemporalEvolutionAnalyzer
        ] = None,
        observation_builder: Optional[
            TemporalObservationBuilder
        ] = None,
    ):
        self.analyzer = (
            analyzer or TemporalEvolutionAnalyzer()
        )
        self.observation_builder = (
            observation_builder
            or TemporalObservationBuilder()
        )

    def build_observation(
        self,
        view: ViewMention,
        observation_date: Optional[str],
        source_id: Optional[int] = None,
        evidence_id: Optional[int] = None,
    ) -> TemporalObservation:
        return self.observation_builder.build_from_view(
            view=view,
            observation_date=observation_date,
            source_id=source_id,
            evidence_id=evidence_id,
        )

    def analyze(
        self,
        observations: List[TemporalObservation],
    ) -> TemporalEvolutionResult:
        return self.analyzer.analyze(
            observations
        )