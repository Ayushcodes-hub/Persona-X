from engine.analysis.dossier_schemas import (
    DossierFinding,
    DossierSection,
)
from engine.analysis.dossier_service import DossierService
from engine.analysis.dossier_synthesizer import DossierSynthesizer


def make_section(
    key,
    title,
    content,
    evidence_ids=None,
    source_ids=None,
    confidence=None,
):
    return DossierSection(
        key=key,
        title=title,
        content=content,
        evidence_ids=evidence_ids or [],
        source_ids=source_ids or [],
        confidence=confidence,
    )


def make_finding(
    finding_type,
    title,
    description,
    evidence_ids=None,
    source_ids=None,
    confidence=None,
):
    return DossierFinding(
        finding_type=finding_type,
        title=title,
        description=description,
        evidence_ids=evidence_ids or [],
        source_ids=source_ids or [],
        confidence=confidence,
    )


def test_sections_are_ordered():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "career",
                "Career",
                "Career information.",
            ),
            make_section(
                "identity",
                "Identity",
                "Identity information.",
            ),
            make_section(
                "timeline",
                "Timeline",
                "Timeline information.",
            ),
        ],
    )

    assert [section.key for section in result.sections] == [
        "identity",
        "career",
        "timeline",
    ]


def test_evidence_and_sources_are_deduplicated():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "identity",
                "Identity",
                "Identity.",
                evidence_ids=[1, 2],
                source_ids=[10],
            ),
            make_section(
                "career",
                "Career",
                "Career.",
                evidence_ids=[2, 3],
                source_ids=[10, 11],
            ),
        ],
        evidence_count=0,
        source_count=0,
    )

    assert result.evidence_count == 3
    assert result.source_count == 2


def test_explicit_counts_are_preserved_when_larger():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "identity",
                "Identity",
                "Identity.",
                evidence_ids=[1],
                source_ids=[10],
            )
        ],
        evidence_count=25,
        source_count=8,
    )

    assert result.evidence_count == 25
    assert result.source_count == 8


def test_evidence_coverage_is_calculated():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "identity",
                "Identity",
                "Supported.",
                evidence_ids=[1],
            ),
            make_section(
                "career",
                "Career",
                "Unsupported.",
            ),
        ],
    )

    assert result.evidence_coverage_score == 0.5


def test_confidence_is_calculated():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "identity",
                "Identity",
                "Identity.",
                confidence=0.9,
            ),
            make_section(
                "career",
                "Career",
                "Career.",
                confidence=0.8,
            ),
        ],
    )

    assert result.confidence == 0.85


def test_findings_contribute_to_evidence_coverage():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "identity",
                "Identity",
                "Identity.",
            )
        ],
        findings=[
            make_finding(
                "achievement",
                "Achievement",
                "Documented achievement.",
                evidence_ids=[100],
            )
        ],
    )

    assert result.evidence_coverage_score == 0.5


def test_political_analysis_flag_is_preserved():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        political_analysis_included=True,
    )

    assert result.political_analysis_included is True


def test_limitations_are_preserved():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        limitations=[
            "Some historical sources were unavailable.",
            "Political evidence was insufficient.",
        ],
    )

    assert len(result.limitations) == 2
    assert "historical" in result.limitations[0]


def test_summary_contains_core_counts():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        professions=["scientist"],
        source_count=10,
        evidence_count=20,
    )

    assert "Example Person" in result.executive_summary
    assert "scientist" in result.executive_summary
    assert "20 evidence records" in result.executive_summary
    assert "10 sources" in result.executive_summary


def test_renderer_produces_readable_dossier():
    service = DossierService()

    dossier = service.build(
        person_name="Example Person",
        professions=["scientist"],
        sections=[
            make_section(
                "identity",
                "Identity",
                "Identity information.",
                evidence_ids=[1],
            ),
            make_section(
                "career",
                "Career",
                "Career information.",
                evidence_ids=[2],
            ),
        ],
        findings=[
            make_finding(
                "achievement",
                "Major Achievement",
                "A documented achievement.",
                evidence_ids=[3],
            )
        ],
    )

    output = service.render(dossier)

    assert "# Example Person" in output
    assert "## Executive Summary" in output
    assert "## Identity" in output
    assert "## Career" in output
    assert "## Evidence-Backed Findings" in output
    assert "Major Achievement" in output


def test_empty_dossier_is_valid():
    service = DossierService()

    dossier = service.build(
        person_name="Unknown Person",
    )

    assert dossier.person_name == "Unknown Person"
    assert dossier.sections == []
    assert dossier.findings == []
    assert dossier.completeness_score == 0.0
    assert dossier.evidence_coverage_score == 0.0


def test_unknown_sections_are_kept_after_known_sections():
    synthesizer = DossierSynthesizer()

    result = synthesizer.synthesize(
        person_name="Example Person",
        sections=[
            make_section(
                "custom_section",
                "Custom",
                "Custom information.",
            ),
            make_section(
                "identity",
                "Identity",
                "Identity.",
            ),
        ],
    )

    assert result.sections[0].key == "identity"
    assert result.sections[1].key == "custom_section"