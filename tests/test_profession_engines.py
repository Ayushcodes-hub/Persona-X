from engine.profession.registry import (
    get_capabilities,
    normalize_profession,
)
from engine.profession.router import ProfessionRouter
from engine.profession.schemas import ProfessionEvidence
from engine.profession.service import ProfessionAnalysisService


def make_evidence():
    return [
        ProfessionEvidence(
            category="records",
            value="International record",
            evidence_id=1,
            source_id=10,
            confidence=0.9,
        ),
        ProfessionEvidence(
            category="awards",
            value="Major award",
            evidence_id=2,
            source_id=11,
            confidence=0.8,
        ),
        ProfessionEvidence(
            category="research",
            value="Published research",
            evidence_id=3,
            source_id=12,
            confidence=0.95,
        ),
        ProfessionEvidence(
            category="companies",
            value="Founded a company",
            evidence_id=4,
            source_id=13,
            confidence=0.85,
        ),
        ProfessionEvidence(
            category="legislation",
            value="Participated in legislation",
            evidence_id=5,
            source_id=14,
            confidence=0.9,
        ),
    ]


def test_profession_normalization():
    assert normalize_profession("cricketer") == "athlete"
    assert normalize_profession("actress") == "actor"
    assert normalize_profession("researcher") == "scientist"
    assert normalize_profession("founder") == "entrepreneur"
    assert normalize_profession("professor") == "academic"


def test_capabilities_exist():
    assert "records" in get_capabilities("athlete")
    assert "research" in get_capabilities("scientist")
    assert "companies" in get_capabilities("entrepreneur")


def test_router_returns_specialized_analyzer():
    router = ProfessionRouter()

    assert router.get_analyzer("athlete").profession == "athlete"
    assert router.get_analyzer("scientist").profession == "scientist"
    assert router.get_analyzer("unknown-profession").profession == "generic"


def test_athlete_analysis():
    router = ProfessionRouter()

    evidence = [
        ProfessionEvidence(
            category="records",
            value="International record",
            evidence_id=1,
            source_id=10,
            confidence=0.9,
        )
    ]

    findings = router.analyze(
        ["athlete"],
        evidence,
    )

    assert len(findings) == 1
    assert findings[0].profession == "athlete"
    assert findings[0].category == "records"
    assert findings[0].evidence_ids == [1]


def test_scientist_analysis():
    router = ProfessionRouter()

    evidence = [
        ProfessionEvidence(
            category="research",
            value="Published research",
            evidence_id=2,
            source_id=20,
            confidence=0.95,
        )
    ]

    findings = router.analyze(
        ["scientist"],
        evidence,
    )

    assert len(findings) == 1
    assert findings[0].profession == "scientist"
    assert findings[0].category == "research"


def test_entrepreneur_analysis():
    router = ProfessionRouter()

    evidence = [
        ProfessionEvidence(
            category="companies",
            value="Founded a company",
            evidence_id=3,
            source_id=30,
            confidence=0.9,
        )
    ]

    findings = router.analyze(
        ["entrepreneur"],
        evidence,
    )

    assert len(findings) == 1
    assert findings[0].profession == "entrepreneur"


def test_politician_analysis():
    router = ProfessionRouter()

    evidence = [
        ProfessionEvidence(
            category="legislation",
            value="Participated in legislation",
            evidence_id=4,
            source_id=40,
            confidence=0.9,
        )
    ]

    findings = router.analyze(
        ["politician"],
        evidence,
    )

    assert len(findings) == 1
    assert findings[0].profession == "politician"


def test_multi_profession_analysis():
    service = ProfessionAnalysisService()

    evidence = [
        ProfessionEvidence(
            category="records",
            value="Sports record",
            evidence_id=1,
            source_id=10,
            confidence=0.9,
        ),
        ProfessionEvidence(
            category="companies",
            value="Founded company",
            evidence_id=2,
            source_id=20,
            confidence=0.8,
        ),
    ]

    result = service.analyze(
        person_name="Multi Profession Person",
        professions=["cricketer", "founder"],
        evidence=evidence,
    )

    assert result.professions == [
        "athlete",
        "entrepreneur",
    ]

    assert len(result.profiles) == 2
    assert result.evidence_count == 2


def test_duplicate_professions_are_removed():
    service = ProfessionAnalysisService()

    result = service.analyze(
        person_name="Person",
        professions=[
            "athlete",
            "cricketer",
            "sportsperson",
        ],
        evidence=[],
    )

    assert result.professions == ["athlete"]


def test_profile_confidence():
    router = ProfessionRouter()

    evidence = [
        ProfessionEvidence(
            category="records",
            value="Record",
            confidence=0.8,
        ),
        ProfessionEvidence(
            category="awards",
            value="Award",
            confidence=1.0,
        ),
    ]

    profiles = router.build_profiles(
        ["athlete"],
        evidence,
    )

    assert len(profiles) == 1
    assert profiles[0].confidence == 0.9


def test_empty_evidence():
    service = ProfessionAnalysisService()

    result = service.analyze(
        person_name="Unknown Person",
        professions=["scientist"],
        evidence=[],
    )

    assert result.evidence_count == 0
    assert result.confidence == 0.0
    assert result.findings == []


def test_generic_fallback():
    router = ProfessionRouter()

    evidence = [
        ProfessionEvidence(
            category="career",
            value="Professional career",
            evidence_id=100,
            source_id=200,
            confidence=0.7,
        )
    ]

    findings = router.analyze(
        ["unknown profession"],
        evidence,
    )

    assert len(findings) == 1
    assert findings[0].profession == "generic"