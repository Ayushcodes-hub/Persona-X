from engine.identity.schemas import IdentityCandidate
from engine.research.planning_service import ResearchPlanningService


def verified_bumrah_candidate():
    return IdentityCandidate(
        name="Jasprit Bumrah",
        profession="athlete",
        nationality="India",
        organization="India national cricket team",
        location="India",
        birth_date="1993-12-06",
    )


def test_resolved_identity_flows_through_complete_pipeline():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        candidates=[verified_bumrah_candidate()],
    )

    assert result.identity_resolution.status == "resolved"
    assert result.identity_resolution.canonical_name == "Jasprit Bumrah"
    assert result.identity_context_verified is True

    assert result.task_count > 0
    assert result.query_count > 0
    assert len(result.query_bundles) == result.task_count


def test_verified_identity_context_reaches_generated_queries():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        candidates=[verified_bumrah_candidate()],
    )

    assert result.query_bundles

    all_variants = [
        variant
        for bundle in result.query_bundles
        for variant in bundle.variants
    ]

    assert all_variants

    enriched_variants = [
        variant
        for variant in all_variants
        if variant.disambiguation_context
    ]

    assert enriched_variants

    assert any(
        "athlete" in variant.disambiguation_context
        for variant in enriched_variants
    )

    assert any(
        "India national cricket team"
        in variant.disambiguation_context
        for variant in enriched_variants
    )


def test_resolved_identity_uses_canonical_name_for_planning():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        candidates=[verified_bumrah_candidate()],
    )

    assert result.identity_resolution.status == "resolved"
    assert result.identity_resolution.canonical_name == "Jasprit Bumrah"
    assert result.research_plan.person_name == "Jasprit Bumrah"


def test_unresolved_identity_does_not_create_verified_context():
    service = ResearchPlanningService()

    result = service.build_plan("Unknown Person")

    assert result.identity_resolution.status == "unresolved"
    assert result.identity_resolution.canonical_name is None
    assert result.identity_context_verified is False


def test_unresolved_identity_still_produces_generic_research_plan():
    service = ResearchPlanningService()

    result = service.build_plan("Unknown Person")

    assert result.task_count == 10
    assert result.query_count > 0

    for bundle in result.query_bundles:
        for variant in bundle.variants:
            assert "Unknown Person" in variant.query_text


def test_verified_profession_can_supply_planner_profession():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        candidates=[verified_bumrah_candidate()],
    )

    assert "athlete" in result.research_plan.professions


def test_explicit_profession_is_preserved_without_identity_candidates():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        professions=["cricketer"],
    )

    assert result.identity_resolution.status == "unresolved"
    assert result.identity_context_verified is False
    assert result.task_count > 0


def test_query_bundle_count_matches_task_count():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        candidates=[verified_bumrah_candidate()],
    )

    assert len(result.query_bundles) == result.task_count


def test_query_count_equals_sum_of_bundle_queries():
    service = ResearchPlanningService()

    result = service.build_plan(
        "Jasprit Bumrah",
        candidates=[verified_bumrah_candidate()],
    )

    expected_count = sum(
        bundle.query_count
        for bundle in result.query_bundles
    )

    assert result.query_count == expected_count


def test_no_identity_facts_are_invented_for_unresolved_person():
    service = ResearchPlanningService()

    result = service.build_plan("Unknown Person")

    for bundle in result.query_bundles:
        for variant in bundle.variants:
            assert variant.disambiguation_context == (
                None
                if not result.research_plan.professions
                else variant.disambiguation_context
            )