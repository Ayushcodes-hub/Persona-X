from engine.analysis.temporal_analyzer import (
    TemporalEvolutionAnalyzer,
)
from engine.analysis.temporal_classifier import (
    TemporalClassifier,
)
from engine.analysis.temporal_observation import (
    TemporalObservationBuilder,
)
from engine.analysis.temporal_schemas import (
    TemporalObservation,
)
from engine.analysis.temporal_service import (
    TemporalEvolutionService,
)
from engine.analysis.topic_schemas import ViewMention


def observation(
    topic="healthcare",
    date="2020-01-01",
    position="supportive",
    position_type="support",
    evidence_id=None,
):
    return TemporalObservation(
        topic=topic,
        observation_date=date,
        position=position,
        position_type=position_type,
        source_text="Documented source text.",
        evidence_id=evidence_id,
        context="interview",
        attribution_status="direct_quote",
        confidence=0.90,
    )


def test_classifier_identifies_stable_position():
    classifier = TemporalClassifier()

    change_type, confidence, explanation = classifier.classify(
        "supportive",
        "supportive",
    )

    assert change_type == "stable"
    assert confidence > 0.9
    assert explanation


def test_classifier_identifies_support_to_opposition_change():
    classifier = TemporalClassifier()

    change_type, confidence, explanation = classifier.classify(
        "supportive",
        "opposed",
    )

    assert change_type == "changed"
    assert confidence >= 0.9
    assert explanation


def test_classifier_identifies_opposition_to_support_change():
    classifier = TemporalClassifier()

    change_type, confidence, explanation = classifier.classify(
        "opposed",
        "supportive",
    )

    assert change_type == "changed"
    assert confidence >= 0.9


def test_classifier_handles_missing_position():
    classifier = TemporalClassifier()

    change_type, confidence, explanation = classifier.classify(
        None,
        "supportive",
    )

    assert change_type == "insufficient_evidence"
    assert confidence < 0.5


def test_analyzer_orders_observations_chronologically():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(date="2024-01-01"),
            observation(date="2019-01-01"),
            observation(date="2022-01-01"),
        ]
    )

    analysis = result.analyses[0]

    dates = [
        item.observation_date
        for item in analysis.observations
    ]

    assert dates == [
        "2019-01-01",
        "2022-01-01",
        "2024-01-01",
    ]


def test_analyzer_detects_documented_change():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(
                date="2018-01-01",
                position="supportive",
                evidence_id=1,
            ),
            observation(
                date="2024-01-01",
                position="opposed",
                evidence_id=2,
            ),
        ]
    )

    analysis = result.analyses[0]

    assert analysis.status == "documented_change"
    assert analysis.change_count == 1

    change = analysis.changes[0]

    assert change.change_type == "changed"
    assert change.earlier_evidence_id == 1
    assert change.later_evidence_id == 2


def test_analyzer_detects_stable_position():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(
                date="2018-01-01",
                position="supportive",
            ),
            observation(
                date="2020-01-01",
                position="supportive",
            ),
            observation(
                date="2024-01-01",
                position="supportive",
            ),
        ]
    )

    analysis = result.analyses[0]

    assert analysis.status == "stable"
    assert analysis.change_count == 2

    assert all(
        change.change_type == "stable"
        for change in analysis.changes
    )


def test_missing_date_does_not_establish_temporal_change():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(
                date="2018-01-01",
                position="supportive",
            ),
            observation(
                date=None,
                position="opposed",
            ),
        ]
    )

    analysis = result.analyses[0]

    assert analysis.observation_count == 1
    assert analysis.change_count == 0
    assert analysis.status == "single_observation"


def test_empty_observations_are_insufficient():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze([])

    assert result.topic_count == 0
    assert result.change_count == 0


def test_topic_groups_are_analyzed_independently():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(
                topic="healthcare",
                date="2020-01-01",
                position="supportive",
            ),
            observation(
                topic="healthcare",
                date="2024-01-01",
                position="opposed",
            ),
            observation(
                topic="education_policy",
                date="2020-01-01",
                position="supportive",
            ),
            observation(
                topic="education_policy",
                date="2024-01-01",
                position="supportive",
            ),
        ]
    )

    assert result.topic_count == 2

    healthcare = next(
        analysis
        for analysis in result.analyses
        if analysis.topic == "healthcare"
    )

    education = next(
        analysis
        for analysis in result.analyses
        if analysis.topic == "education_policy"
    )

    assert healthcare.status == "documented_change"
    assert education.status == "stable"


def test_observation_builder_preserves_evidence_identity():
    builder = TemporalObservationBuilder()

    view = ViewMention(
        topic="healthcare",
        position="supportive",
        position_type="support",
        context="interview",
        supporting_text="I support healthcare access.",
        attribution_status="direct_quote",
        confidence=0.90,
    )

    result = builder.build_from_view(
        view=view,
        observation_date="2024-05-01",
        source_id=10,
        evidence_id=20,
    )

    assert result.topic == "healthcare"
    assert result.observation_date == "2024-05-01"
    assert result.source_id == 10
    assert result.evidence_id == 20
    assert result.position == "supportive"


def test_service_builds_and_analyzes_observations():
    service = TemporalEvolutionService()

    first_view = ViewMention(
        topic="energy",
        position="supportive",
        position_type="support",
        supporting_text="I support renewable energy.",
        attribution_status="direct_quote",
        confidence=0.90,
    )

    second_view = ViewMention(
        topic="energy",
        position="opposed",
        position_type="oppose",
        supporting_text="I oppose this energy policy.",
        attribution_status="direct_quote",
        confidence=0.90,
    )

    first = service.build_observation(
        first_view,
        "2018-01-01",
        evidence_id=101,
    )

    second = service.build_observation(
        second_view,
        "2025-01-01",
        evidence_id=202,
    )

    result = service.analyze(
        [second, first]
    )

    assert result.topic_count == 1
    assert result.change_count == 1

    change = result.analyses[0].changes[0]

    assert change.earlier_evidence_id == 101
    assert change.later_evidence_id == 202


def test_invalid_date_is_ignored_for_temporal_ordering():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(
                date="not-a-date",
                position="supportive",
            ),
            observation(
                date="2024-01-01",
                position="supportive",
            ),
        ]
    )

    analysis = result.analyses[0]

    assert analysis.observation_count == 1
    assert analysis.status == "single_observation"


def test_temporal_change_preserves_source_evidence():
    analyzer = TemporalEvolutionAnalyzer()

    result = analyzer.analyze(
        [
            observation(
                date="2010-01-01",
                position="opposed",
                evidence_id=11,
            ),
            observation(
                date="2020-01-01",
                position="supportive",
                evidence_id=22,
            ),
        ]
    )

    change = result.analyses[0].changes[0]

    assert change.earlier_evidence_id == 11
    assert change.later_evidence_id == 22
    assert change.confidence >= 0.9