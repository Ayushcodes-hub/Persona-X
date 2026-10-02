from engine.political.schemas import PoliticalEvidence
from engine.political.service import PoliticalAnalysisService
from engine.political.spectrum_analyzer import PoliticalSpectrumAnalyzer


def test_insufficient_political_evidence_yields_no_spectrum():
    service = PoliticalAnalysisService()
    result = service.analyze(
        person_name="Jasprit Bumrah",
        evidence=[],
    )

    assert result.applicable is False
    assert result.spectrum is not None
    assert result.spectrum.applicable is False
    assert result.spectrum.spectrum_score is None
    assert "Insufficient" in result.spectrum.spectrum_label
    assert "insufficient verified policy positions" in result.spectrum.rationale


def test_left_leaning_economic_and_social_positions():
    service = PoliticalAnalysisService()
    evidence = [
        PoliticalEvidence(
            evidence_type="policy_statement",
            text="I strongly support expanding universal healthcare and increasing funding for social welfare.",
            topic="social_policy",
            issue="healthcare",
            position="support",
            confidence=0.95,
        ),
        PoliticalEvidence(
            evidence_type="policy_statement",
            text="We must protect civil rights for all citizens and advance legal equality protections.",
            topic="social_policy",
            issue="civil_rights",
            position="support",
            confidence=0.95,
        ),
        PoliticalEvidence(
            evidence_type="policy_statement",
            text="Corporate taxes should be raised to fund public infrastructure and schools.",
            topic="economic_policy",
            issue="taxation",
            position="support",
            confidence=0.95,
        ),
    ]

    result = service.analyze(
        person_name="Jane Reformer",
        evidence=evidence,
    )

    assert result.applicable is True
    assert result.spectrum is not None
    assert result.spectrum.applicable is True
    assert result.spectrum.spectrum_score < -0.20  # Explicitly left of center
    assert "Left" in result.spectrum.spectrum_label or "Progressive" in result.spectrum.spectrum_label
    assert result.spectrum.economic_axis < 0.0
    assert result.spectrum.social_axis < 0.0
    assert len(result.spectrum.key_indicators) > 0


def test_right_leaning_market_and_traditionalist_positions():
    service = PoliticalAnalysisService()
    evidence = [
        PoliticalEvidence(
            evidence_type="policy_statement",
            text="We must cut taxes, reduce corporate regulation, and restrain government spending.",
            topic="economic_policy",
            issue="taxation",
            position="oppose",
            confidence=0.95,
        ),
        PoliticalEvidence(
            evidence_type="policy_statement",
            text="Excessive business regulation stifles enterprise autonomy and economic growth.",
            topic="economic_policy",
            issue="business_regulation",
            position="oppose",
            confidence=0.95,
        ),
        PoliticalEvidence(
            evidence_type="policy_statement",
            text="We need strict border security and robust defense spending to secure our nation.",
            topic="foreign_policy",
            issue="defense",
            position="support",
            confidence=0.95,
        ),
    ]

    result = service.analyze(
        person_name="John Conservative",
        evidence=evidence,
    )

    assert result.applicable is True
    assert result.spectrum is not None
    assert result.spectrum.applicable is True
    assert result.spectrum.spectrum_score > 0.20  # Explicitly right of center
    assert "Right" in result.spectrum.spectrum_label or "Conservative" in result.spectrum.spectrum_label
    assert result.spectrum.economic_axis > 0.0
    assert len(result.spectrum.key_indicators) > 0
