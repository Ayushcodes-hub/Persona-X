import pytest
from engine.identity.discovery import IdentityDiscoveryService


def test_infer_profession_from_text():
    service = IdentityDiscoveryService()
    assert service._infer_profession_from_text("Indian cricketer (born 1993)") == "athlete"
    assert service._infer_profession_from_text("French-Polish physicist and chemist") == "scientist"
    assert service._infer_profession_from_text("American film actor and producer") == "actor"
    assert service._infer_profession_from_text("Tech entrepreneur and investor") == "entrepreneur"
    assert service._infer_profession_from_text("British politician and Member of Parliament") == "politician"


def test_infer_nationality_from_text():
    service = IdentityDiscoveryService()
    assert service._infer_nationality_from_text("Indian cricketer") == "India"
    assert service._infer_nationality_from_text("French physicist") == "France"
    assert service._infer_nationality_from_text("American actor") == "United States"


def test_fallback_candidate_when_query_is_clean():
    service = IdentityDiscoveryService()
    candidates = service.discover_candidates("Some Unlikely Person Name 99283")
    assert len(candidates) >= 1
    assert candidates[0].name == "Some Unlikely Person Name 99283"
    assert candidates[0].match_score > 0.0
