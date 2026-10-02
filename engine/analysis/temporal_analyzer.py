from collections import defaultdict
from datetime import date
from typing import Dict, List, Tuple

from engine.analysis.temporal_classifier import TemporalClassifier
from engine.analysis.temporal_schemas import (
    TemporalChange,
    TemporalEvolutionResult,
    TemporalObservation,
    TemporalTopicAnalysis,
)


class TemporalEvolutionAnalyzer:
    """
    Performs evidence-backed chronological analysis.

    Rules:

    1. Undated observations are retained but cannot establish chronology.
    2. Each topic is analyzed independently.
    3. Observations are sorted by explicit date.
    4. Adjacent dated observations are compared.
    5. Missing observations are never treated as evidence of change.
    """

    def __init__(
        self,
        classifier=None,
    ):
        self.classifier = (
            classifier or TemporalClassifier()
        )

    @staticmethod
    def _parse_date(value: str) -> date:
        return date.fromisoformat(value)

    def _dated_observations(
        self,
        observations: List[TemporalObservation],
    ) -> List[TemporalObservation]:
        valid: List[
            Tuple[date, TemporalObservation]
        ] = []

        for observation in observations:
            if not observation.observation_date:
                continue

            try:
                parsed = self._parse_date(
                    observation.observation_date
                )
            except ValueError:
                continue

            valid.append((parsed, observation))

        valid.sort(key=lambda item: item[0])

        return [
            observation
            for _, observation in valid
        ]

    def analyze_topic(
        self,
        topic: str,
        observations: List[TemporalObservation],
    ) -> TemporalTopicAnalysis:
        topic_observations = [
            observation
            for observation in observations
            if observation.topic == topic
        ]

        dated = self._dated_observations(
            topic_observations
        )

        analysis = TemporalTopicAnalysis(
            topic=topic,
            observations=dated,
        )

        if len(dated) == 0:
            analysis.status = "insufficient_evidence"
            return analysis

        if len(dated) == 1:
            analysis.status = "single_observation"
            return analysis

        changes: List[TemporalChange] = []

        for earlier, later in zip(
            dated,
            dated[1:],
        ):
            (
                change_type,
                confidence,
                explanation,
            ) = self.classifier.classify(
                earlier_position=earlier.position,
                later_position=later.position,
            )

            changes.append(
                TemporalChange(
                    topic=topic,
                    earlier_date=earlier.observation_date,
                    later_date=later.observation_date,
                    earlier_position=earlier.position,
                    later_position=later.position,
                    earlier_position_type=earlier.position_type,
                    later_position_type=later.position_type,
                    change_type=change_type,
                    explanation=explanation,
                    earlier_evidence_id=earlier.evidence_id,
                    later_evidence_id=later.evidence_id,
                    confidence=confidence,
                )
            )

        analysis.changes = changes

        if any(
            change.change_type == "changed"
            for change in changes
        ):
            analysis.status = "documented_change"
        elif all(
            change.change_type == "stable"
            for change in changes
        ):
            analysis.status = "stable"
        else:
            analysis.status = "mixed_or_insufficient"

        return analysis

    def analyze(
        self,
        observations: List[TemporalObservation],
    ) -> TemporalEvolutionResult:
        grouped: Dict[
            str,
            List[TemporalObservation],
        ] = defaultdict(list)

        for observation in observations:
            grouped[observation.topic].append(
                observation
            )

        analyses: List[TemporalTopicAnalysis] = []

        for topic in sorted(grouped):
            analyses.append(
                self.analyze_topic(
                    topic=topic,
                    observations=grouped[topic],
                )
            )

        return TemporalEvolutionResult(
            analyses=analyses
        )