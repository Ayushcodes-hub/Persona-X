from engine.analysis.claim_normalizer import (
    ClaimNormalizer,
)
from engine.analysis.contradiction_analyzer import (
    ContradictionAnalyzer,
)
from engine.analysis.contradiction_classifier import (
    ContradictionClassifier,
)
from engine.analysis.contradiction_schemas import (
    ClaimObservation,
)
from engine.analysis.contradiction_service import (
    ContradictionAnalysisService,
)


def claim(
    text="The person supports healthcare expansion.",
    topic="healthcare",
    subject="healthcare expansion",
    predicate="position",
    object_value="healthcare expansion",
    date="2020-01-01",
    polarity="supportive",
    evidence_id=1,
):
    return ClaimObservation(
        claim_text=text,
        topic=topic,
        subject=subject,
        predicate=predicate,
        object_value=object_value,
        observation_date=date,
        context="public_statement",
        position=polarity,
        polarity=polarity,
        evidence_id=evidence_id,
        source_id=10,
        verification_status="unverified",
        confidence=0.90,
    )


def test_normalizer_normalizes_whitespace_and_case():
    normalizer = ClaimNormalizer()

    assert (
        normalizer.normalize_text(
            "  Healthcare   Expansion  "
        )
        == "healthcare expansion"
    )


def test_normalizer_normalizes_polarity():
    normalizer = ClaimNormalizer()

    assert (
        normalizer.normalize_polarity("support")
        == "supportive"
    )

    assert (
        normalizer.normalize_polarity("against")
        == "opposed"
    )


def test_classifier_detects_opposing_structured_claims():
    classifier = ContradictionClassifier()

    first = claim(
        date="2018-01-01",
        polarity="supportive",
        evidence_id=1,
    )

    second = claim(
        text="The person opposes healthcare expansion.",
        date="2025-01-01",
        polarity="opposed",
        evidence_id=2,
    )

    result = classifier.classify(
        first,
        second,
    )

    assert result[0] == "potential_inconsistency"
    assert result[1] >= 0.9
    assert result[3] is True
    assert result[4] is True
    assert result[5] is True
    assert result[6] is True


def test_classifier_does_not_flag_different_topics():
    classifier = ContradictionClassifier()

    first = claim(
        topic="healthcare",
        subject="healthcare expansion",
        polarity="supportive",
    )

    second = claim(
        topic="education_policy",
        subject="education funding",
        polarity="opposed",
    )

    result = classifier.classify(
        first,
        second,
    )

    assert result[0] == "compatible"


def test_classifier_does_not_flag_different_subjects():
    classifier = ContradictionClassifier()

    first = claim(
        topic="healthcare",
        subject="public healthcare",
        polarity="supportive",
    )

    second = claim(
        topic="healthcare",
        subject="private healthcare",
        polarity="opposed",
    )

    result = classifier.classify(
        first,
        second,
    )

    assert result[0] == "compatible"


def test_classifier_requires_structured_proposition():
    classifier = ContradictionClassifier()

    first = ClaimObservation(
        claim_text="I support healthcare.",
        topic="healthcare",
        subject="healthcare",
        polarity="supportive",
    )

    second = ClaimObservation(
        claim_text="I oppose healthcare.",
        topic="healthcare",
        subject="healthcare",
        polarity="opposed",
    )

    result = classifier.classify(
        first,
        second,
    )

    assert result[0] == "insufficient_evidence"


def test_missing_polarity_is_insufficient():
    classifier = ContradictionClassifier()

    first = claim(
        polarity=None,
    )

    second = claim(
        polarity="supportive",
        evidence_id=2,
    )

    result = classifier.classify(
        first,
        second,
    )

    assert result[0] == "insufficient_evidence"


def test_same_position_is_not_inconsistency():
    classifier = ContradictionClassifier()

    first = claim(
        date="2018-01-01",
        polarity="supportive",
    )

    second = claim(
        date="2025-01-01",
        polarity="supportive",
        evidence_id=2,
    )

    result = classifier.classify(
        first,
        second,
    )

    assert result[0] == "insufficient_evidence"
    assert result[6] is False


def test_analyzer_orders_claims_by_date():
    analyzer = ContradictionAnalyzer()

    later = claim(
        date="2025-01-01",
        polarity="opposed",
        evidence_id=2,
    )

    earlier = claim(
        date="2018-01-01",
        polarity="supportive",
        evidence_id=1,
    )

    result = analyzer.compare(
        later,
        earlier,
    )

    assert (
        result.earlier_claim.evidence_id
        == 1
    )

    assert (
        result.later_claim.evidence_id
        == 2
    )


def test_analyzer_detects_potential_inconsistency():
    analyzer = ContradictionAnalyzer()

    first = claim(
        date="2018-01-01",
        polarity="supportive",
        evidence_id=101,
    )

    second = claim(
        text="The person opposes healthcare expansion.",
        date="2025-01-01",
        polarity="opposed",
        evidence_id=202,
    )

    result = analyzer.compare(
        first,
        second,
    )

    assert (
        result.status
        == "potential_inconsistency"
    )

    assert (
        result.earlier_claim.evidence_id
        == 101
    )

    assert (
        result.later_claim.evidence_id
        == 202
    )


def test_analyzer_preserves_evidence_identity():
    analyzer = ContradictionAnalyzer()

    first = claim(
        evidence_id=111,
    )

    second = claim(
        evidence_id=222,
        polarity="opposed",
    )

    result = analyzer.compare(
        first,
        second,
    )

    assert (
        result.earlier_claim.evidence_id
        == 111
    )

    assert (
        result.later_claim.evidence_id
        == 222
    )


def test_pairwise_analysis_counts_all_pairs():
    analyzer = ContradictionAnalyzer()

    claims = [
        claim(
            date="2018-01-01",
            evidence_id=1,
        ),
        claim(
            date="2020-01-01",
            evidence_id=2,
        ),
        claim(
            date="2025-01-01",
            evidence_id=3,
        ),
    ]

    result = analyzer.analyze(
        claims
    )

    assert result.comparison_count == 3


def test_analysis_counts_potential_inconsistencies():
    analyzer = ContradictionAnalyzer()

    claims = [
        claim(
            date="2018-01-01",
            polarity="supportive",
            evidence_id=1,
        ),
        claim(
            date="2020-01-01",
            polarity="opposed",
            evidence_id=2,
        ),
        claim(
            date="2025-01-01",
            polarity="supportive",
            evidence_id=3,
        ),
    ]

    result = analyzer.analyze(
        claims
    )

    assert result.comparison_count == 3
    assert (
        result.potential_inconsistency_count
        == 2
    )


def test_service_exposes_compare():
    service = ContradictionAnalysisService()

    first = claim(
        date="2018-01-01",
        polarity="supportive",
    )

    second = claim(
        date="2025-01-01",
        polarity="opposed",
        evidence_id=2,
    )

    result = service.compare(
        first,
        second,
    )

    assert (
        result.status
        == "potential_inconsistency"
    )


def test_service_exposes_full_analysis():
    service = ContradictionAnalysisService()

    result = service.analyze(
        [
            claim(
                date="2018-01-01",
                polarity="supportive",
            ),
            claim(
                date="2025-01-01",
                polarity="opposed",
                evidence_id=2,
            ),
        ]
    )

    assert result.comparison_count == 1
    assert (
        result.potential_inconsistency_count
        == 1
    )