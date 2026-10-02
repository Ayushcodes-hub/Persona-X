from engine.political.schemas import PoliticalEvidence
from engine.political.service import PoliticalAnalysisService
from engine.political.sufficiency import PoliticalSufficiencyAnalyzer


def evidence(
    evidence_type,
    text,
    topic=None,
    issue=None,
    position=None,
    evidence_id=None,
    source_id=None,
    event_date=None,
    confidence=0.9,
):
    return PoliticalEvidence(
        evidence_type=evidence_type,
        text=text,
        topic=topic,
        issue=issue,
        position=position,
        evidence_id=evidence_id,
        source_id=source_id,
        event_date=event_date,
        confidence=confidence,
        verification_status="verified",
        attribution_status="direct",
    )


def test_no_political_evidence_is_insufficient():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Nonpolitical Person",
        [],
    )

    assert result.applicable is False
    assert result.sufficiency.sufficient is False
    assert result.dimensions == []
    assert result.confidence == 0.0


def test_single_weak_political_reference_is_insufficient():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "secondary_analysis",
                "An article discusses the person's politics.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                confidence=0.4,
            )
        ],
    )

    assert result.applicable is False
    assert result.sufficiency.sufficient is False


def test_two_direct_political_items_are_sufficient():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "The person explicitly discussed taxation.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=1,
                source_id=10,
            ),
            evidence(
                "political_interview",
                "The person discussed healthcare policy.",
                topic="social_policy",
                issue="healthcare",
                position="support",
                evidence_id=2,
                source_id=20,
            ),
        ],
    )

    assert result.applicable is True
    assert result.sufficiency.sufficient is True
    assert result.sufficiency.qualifying_evidence_count == 2


def test_position_is_grouped_by_dimension_and_issue():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Taxation statement",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=1,
            ),
            evidence(
                "policy_statement",
                "Healthcare statement",
                topic="social_policy",
                issue="healthcare",
                position="oppose",
                evidence_id=2,
            ),
        ],
    )

    assert len(result.dimensions) == 2

    economic = next(
        item
        for item in result.dimensions
        if item.name == "economic_policy"
    )

    assert len(economic.positions) == 1
    assert economic.positions[0].issue == "taxation"
    assert economic.positions[0].position == "support"


def test_political_activity_is_preserved():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "party_affiliation",
                "Documented party affiliation.",
                topic="political_identity",
                issue="party_affiliation",
                position="support",
                evidence_id=1,
            ),
            evidence(
                "political_action",
                "Participated in a political campaign.",
                topic="political_identity",
                issue="campaign_activity",
                evidence_id=2,
            ),
        ],
    )

    assert len(result.political_activity) == 2


def test_temporal_potential_inconsistency():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Earlier position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=101,
                event_date="2018-01-01",
            ),
            evidence(
                "policy_statement",
                "Later position.",
                topic="economic_policy",
                issue="taxation",
                position="oppose",
                evidence_id=202,
                event_date="2025-01-01",
            ),
        ],
    )

    assert len(result.conflicts) == 1

    conflict = result.conflicts[0]

    assert conflict.classification == "potential_inconsistency"
    assert conflict.earlier_position == "support"
    assert conflict.later_position == "oppose"
    assert conflict.earlier_date == "2018-01-01"
    assert conflict.later_date == "2025-01-01"


def test_same_position_is_not_conflict():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Earlier position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=101,
                event_date="2018-01-01",
            ),
            evidence(
                "policy_statement",
                "Later position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=202,
                event_date="2025-01-01",
            ),
        ],
    )

    assert result.conflicts == []


def test_different_issue_is_not_conflict():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Taxation position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=101,
                event_date="2018-01-01",
            ),
            evidence(
                "policy_statement",
                "Healthcare position.",
                topic="social_policy",
                issue="healthcare",
                position="oppose",
                evidence_id=202,
                event_date="2025-01-01",
            ),
        ],
    )

    assert result.conflicts == []


def test_missing_dates_do_not_create_temporal_conflict():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Earlier position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=101,
            ),
            evidence(
                "policy_statement",
                "Later position.",
                topic="economic_policy",
                issue="taxation",
                position="oppose",
                evidence_id=202,
            ),
        ],
    )

    assert result.conflicts == []


def test_low_confidence_evidence_is_not_sufficient():
    analyzer = PoliticalSufficiencyAnalyzer()

    result = analyzer.analyze(
        [
            evidence(
                "policy_statement",
                "Statement",
                topic="economic_policy",
                issue="taxation",
                position="support",
                confidence=0.3,
            ),
            evidence(
                "policy_statement",
                "Statement",
                topic="social_policy",
                issue="healthcare",
                position="support",
                confidence=0.4,
            ),
        ]
    )

    assert result.sufficient is False


def test_self_identification_counts_as_direct_evidence():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "self_identification",
                "Explicit political self-identification.",
                topic="political_identity",
                issue="political_self_identification",
                position="support",
                evidence_id=1,
            ),
            evidence(
                "policy_statement",
                "Explicit policy position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=2,
            ),
        ],
    )

    assert result.applicable is True
    assert result.sufficiency.sufficient is True


def test_limitations_are_present_when_conflicts_exist():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Earlier position.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=1,
                event_date="2018-01-01",
            ),
            evidence(
                "policy_statement",
                "Later position.",
                topic="economic_policy",
                issue="taxation",
                position="oppose",
                evidence_id=2,
                event_date="2025-01-01",
            ),
        ],
    )

    assert result.conflicts
    assert any(
        "potential inconsistency" in item.lower()
        for item in result.limitations
    )


def test_evidence_count_is_preserved():
    service = PoliticalAnalysisService()

    result = service.analyze(
        "Person",
        [
            evidence(
                "policy_statement",
                "Statement one.",
                topic="economic_policy",
                issue="taxation",
                position="support",
                evidence_id=1,
            ),
            evidence(
                "policy_statement",
                "Statement two.",
                topic="social_policy",
                issue="healthcare",
                position="oppose",
                evidence_id=2,
            ),
            evidence(
                "political_action",
                "Political action.",
                topic="political_identity",
                issue="campaign_activity",
                evidence_id=3,
            ),
        ],
    )

    assert result.evidence_count == 3