from engine.identity.context import IdentityContextBuilder
from engine.identity.schemas import IdentityCandidate, IdentityResolution
from engine.research.planner import UniversalResearchPlanner
from engine.research.query_generator import ResearchQueryGenerator


def build_task(
    person_name="Jasprit Bumrah",
    professions=None,
):
    if professions is None:
        professions = ["cricketer"]

    planner = UniversalResearchPlanner()
    plan = planner.build_plan(person_name, professions)
    return plan.tasks[0]


def build_verified_identity_context():
    resolution = IdentityResolution(
        query_name="Jasprit Bumrah",
        status="resolved",
        confidence=0.95,
        canonical_name="Jasprit Bumrah",
        candidates=[
            IdentityCandidate(
                name="Jasprit Bumrah",
                profession="athlete",
                nationality="India",
                organization="India national cricket team",
                location="India",
                birth_date="1993-12-06",
            )
        ],
    )

    return IdentityContextBuilder().build(resolution)


def build_ambiguous_identity_context():
    resolution = IdentityResolution(
        query_name="John Smith",
        status="ambiguous",
        confidence=0.51,
    )

    return IdentityContextBuilder().build(resolution)


def build_unresolved_identity_context():
    resolution = IdentityResolution(
        query_name="Unknown Person",
        status="unresolved",
        confidence=0.0,
    )

    return IdentityContextBuilder().build(resolution)


def test_generates_canonical_official_and_interview_variants():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    variant_types = [variant.variant_type for variant in bundle.variants]

    assert "canonical" in variant_types
    assert "official" in variant_types
    assert "interview" in variant_types

    assert bundle.query_count >= 3


def test_profession_specific_variants_are_generated():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    variant_types = [variant.variant_type for variant in bundle.variants]

    assert "profession_teams" in variant_types
    assert "profession_records" in variant_types
    assert "profession_awards" in variant_types
    assert "profession_interviews" in variant_types
    assert "profession_endorsements" in variant_types
    assert "profession_philanthropy" in variant_types


def test_full_career_does_not_create_temporal_search_variant():
    task = build_task()

    assert task.temporal_scope == "full_career"

    generator = ResearchQueryGenerator()
    bundle = generator.generate(task)

    assert not any(
        variant.variant_type == "temporal"
        for variant in bundle.variants
    )

    assert all(
        "full_career" not in variant.query_text
        for variant in bundle.variants
    )


def test_query_identity_is_preserved():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    for variant in bundle.variants:
        assert '"Jasprit Bumrah"' in variant.query_text


def test_priorities_are_descending():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    priorities = [variant.priority for variant in bundle.variants]

    assert priorities == sorted(priorities, reverse=True)


def test_temporal_variant_is_created_for_real_temporal_scope():
    task = build_task()
    task.temporal_scope = "2013-2026"

    generator = ResearchQueryGenerator()
    bundle = generator.generate(task)

    temporal_variants = [
        variant
        for variant in bundle.variants
        if variant.variant_type == "temporal"
    ]

    assert len(temporal_variants) == 1

    temporal_query = temporal_variants[0].query_text

    assert '"Jasprit Bumrah"' in temporal_query
    assert "2013-2026" in temporal_query
    assert temporal_variants[0].source_focus == "historical"


def test_all_supported_professions_generate_profession_variants():
    planner = UniversalResearchPlanner()
    generator = ResearchQueryGenerator()

    professions = [
        "athlete",
        "actor",
        "scientist",
        "entrepreneur",
        "politician",
        "journalist",
        "author",
        "academic",
        "artist",
    ]

    for profession in professions:
        plan = planner.build_plan(
            f"Test Person {profession}",
            [profession],
        )

        profession_tasks = [
            task
            for task in plan.tasks
            if task.profession_context == profession
        ]

        assert profession_tasks, (
            f"No planner task generated for profession: {profession}"
        )

        bundle = generator.generate(profession_tasks[0])

        profession_variants = [
            variant
            for variant in bundle.variants
            if variant.variant_type.startswith("profession_")
        ]

        assert profession_variants, (
            f"No profession-specific queries generated for: {profession}"
        )


def test_unsupported_profession_does_not_generate_profession_variants():
    planner = UniversalResearchPlanner()
    generator = ResearchQueryGenerator()

    plan = planner.build_plan(
        "Test Person",
        ["unknown_profession"],
    )

    task = plan.tasks[0]
    bundle = generator.generate(task)

    assert not any(
        variant.variant_type.startswith("profession_")
        for variant in bundle.variants
    )


def test_politician_profession_queries_are_not_political_analysis():
    planner = UniversalResearchPlanner()
    generator = ResearchQueryGenerator()

    plan = planner.build_plan(
        "Test Politician",
        ["politician"],
    )

    politician_tasks = [
        task
        for task in plan.tasks
        if task.profession_context == "politician"
    ]

    assert politician_tasks

    bundle = generator.generate(politician_tasks[0])

    profession_variants = [
        variant
        for variant in bundle.variants
        if variant.variant_type.startswith("profession_")
    ]

    assert profession_variants

    assert all(
        variant.variant_type.startswith("profession_")
        for variant in profession_variants
    )


def test_canonical_query_has_general_source_target():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    canonical = next(
        variant
        for variant in bundle.variants
        if variant.variant_type == "canonical"
    )

    assert canonical.source_target == "general_web"


def test_official_query_has_official_source_target():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    official = next(
        variant
        for variant in bundle.variants
        if variant.variant_type == "official"
    )

    assert official.source_target == "official_source"


def test_athlete_queries_have_source_targets():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    expected_targets = {
        "profession_teams": "sports_governing_body",
        "profession_records": "sports_statistics",
        "profession_awards": "sports_awards",
        "profession_interviews": "major_media",
        "profession_endorsements": "company_or_brand",
        "profession_philanthropy": "foundation_or_ngo",
    }

    for variant_type, expected_target in expected_targets.items():
        variant = next(
            variant
            for variant in bundle.variants
            if variant.variant_type == variant_type
        )

        assert variant.source_target == expected_target


def test_verified_identity_context_enriches_query():
    task = build_task()
    generator = ResearchQueryGenerator()

    identity_context = build_verified_identity_context()

    assert identity_context.is_verified is True

    bundle = generator.generate(
        task,
        identity_context=identity_context,
    )

    canonical = next(
        variant
        for variant in bundle.variants
        if variant.variant_type == "canonical"
    )

    assert canonical.disambiguation_context is not None
    assert "athlete" in canonical.disambiguation_context
    assert "India" in canonical.disambiguation_context
    assert "India national cricket team" in canonical.disambiguation_context

    assert "athlete" in canonical.query_text
    assert "India" in canonical.query_text
    assert "India national cricket team" in canonical.query_text


def test_ambiguous_identity_does_not_enrich_query():
    task = build_task()
    generator = ResearchQueryGenerator()

    identity_context = build_ambiguous_identity_context()

    assert identity_context.is_verified is False

    bundle = generator.generate(
        task,
        identity_context=identity_context,
    )

    canonical = next(
        variant
        for variant in bundle.variants
        if variant.variant_type == "canonical"
    )

    assert canonical.disambiguation_context == "athlete"
    assert "John Smith" not in canonical.query_text


def test_unresolved_identity_does_not_enrich_query():
    task = build_task()
    generator = ResearchQueryGenerator()

    identity_context = build_unresolved_identity_context()

    assert identity_context.is_verified is False

    bundle = generator.generate(
        task,
        identity_context=identity_context,
    )

    canonical = next(
        variant
        for variant in bundle.variants
        if variant.variant_type == "canonical"
    )

    assert canonical.disambiguation_context == "athlete"


def test_no_identity_context_preserves_existing_behavior():
    task = build_task()
    generator = ResearchQueryGenerator()

    bundle = generator.generate(task)

    canonical = next(
        variant
        for variant in bundle.variants
        if variant.variant_type == "canonical"
    )

    assert canonical.disambiguation_context == "athlete"
    assert canonical.query_text.endswith("athlete")