from typing import Optional

from engine.analysis.temporal_schemas import TemporalObservation
from engine.analysis.topic_schemas import ViewMention


class TemporalObservationBuilder:
    """
    Converts documented views into temporal observations.

    Dates must be explicitly supplied. The builder never invents dates.
    """

    def build_from_view(
        self,
        view: ViewMention,
        observation_date: Optional[str],
        source_id: Optional[int] = None,
        evidence_id: Optional[int] = None,
    ) -> TemporalObservation:
        return TemporalObservation(
            topic=view.topic,
            observation_date=observation_date,
            position=view.position,
            position_type=view.position_type,
            source_text=view.supporting_text,
            source_id=source_id,
            evidence_id=evidence_id,
            context=view.context,
            attribution_status=view.attribution_status,
            confidence=view.confidence,
        )