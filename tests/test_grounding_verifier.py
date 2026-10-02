import pytest
from engine.evidence.grounding_verifier import GroundingVerifier, grounding_verifier


def test_grounding_verifier_exact_match():
    source_text = (
        "In a press conference on Tuesday, the CEO stated that the company will invest "
        "$500 million into renewable clean energy technologies across South Asia over the next three years."
    )
    quote = "the company will invest $500 million into renewable clean energy technologies"

    result = grounding_verifier.verify_span(
        candidate_span=quote,
        source_text=source_text,
        source_tier=1,
        corroborating_source_count=2,
        is_direct_quote=True,
    )

    assert result.is_verified is True
    assert result.status == "verified"
    assert result.span_match_ratio == 1.0
    assert result.confidence >= 0.9
    assert result.statement_taxonomy == "direct_quote"
    assert result.failure_reason is None


def test_grounding_verifier_drops_hallucinated_quote():
    source_text = (
        "The player represented the national team in 45 matches, scoring 12 goals and providing 8 assists."
    )
    hallucinated_quote = "I always knew we would win the championship against all odds."

    result = grounding_verifier.verify_span(
        candidate_span=hallucinated_quote,
        source_text=source_text,
        source_tier=2,
        is_direct_quote=True,
    )

    assert result.is_verified is False
    assert result.status == "unsupported_dropped"
    assert result.confidence == 0.0
    assert "Direct quote or allegation could not be verified" in result.failure_reason


def test_grounding_verifier_allegation_handling():
    source_text = "The department initiated an inquiry into financial irregularities reported in the audit."
    allegation_span = "The minister personally accepted bribes from foreign defense contractors."

    result = grounding_verifier.verify_span(
        candidate_span=allegation_span,
        source_text=source_text,
        source_tier=2,
        is_allegation=True,
    )

    assert result.is_verified is False
    assert result.status == "unsupported_dropped"
    assert result.confidence == 0.0
    assert result.statement_taxonomy == "allegation"


def test_grounding_verifier_fuzzy_punctuation_match():
    source_text = 'The committee observed: "Fiscal discipline remains paramount for long-term growth."'
    quote = 'fiscal discipline remains paramount for long term growth'

    result = grounding_verifier.verify_span(
        candidate_span=quote,
        source_text=source_text,
        source_tier=1,
        is_direct_quote=False,
    )

    assert result.is_verified is True
    assert result.span_match_ratio >= 0.85
    assert result.status == "verified"
