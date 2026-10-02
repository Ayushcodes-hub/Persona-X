from engine.research.planner import UniversalResearchPlanner


def test_empty_person_name_is_rejected():
    planner = UniversalResearchPlanner()

    try:
        planner.build_plan("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Person name cannot be empty" in str(exc)


def test_profession_alias_is_normalized():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Jasprit Bumrah",
        professions=["cricketer"],
    )

    assert plan.professions == ["athlete"]


def test_universal_tasks_are_created():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan("Example Person")

    assert plan.task_count == 10
    assert len(plan.tasks) == 10


def test_athlete_tasks_are_added():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Jasprit Bumrah",
        professions=["cricketer"],
    )

    assert plan.task_count == 16
    assert any(
        task.profession_context is None
        and task.query_type == "identity"
        for task in plan.tasks
    )
    assert any(
        task.profession_context == "athlete"
        and task.query_type == "sporting_career"
        for task in plan.tasks
    )


def test_political_research_is_not_automatically_enabled():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Jasprit Bumrah",
        professions=["cricketer"],
    )

    assert plan.political_research_justified is False
    assert not any(
        task.profession_context == "political_research"
        for task in plan.tasks
    )


def test_multiple_professions_are_combined():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Example Person",
        professions=["entrepreneur", "author"],
    )

    assert plan.professions == ["entrepreneur", "author"]
    assert plan.task_count == 20

    assert any(
        task.profession_context == "entrepreneur"
        for task in plan.tasks
    )

    assert any(
        task.profession_context == "author"
        for task in plan.tasks
    )


def test_political_tasks_require_explicit_justification():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Example Politician",
        professions=["politician"],
        political_research_justified=True,
        political_research_reason="Documented political activity",
    )

    assert plan.political_research_justified is True
    assert plan.political_research_reason == "Documented political activity"

    political_tasks = [
        task
        for task in plan.tasks
        if task.profession_context == "political_research"
    ]

    assert len(political_tasks) == 4


def test_task_priorities_are_sorted_descending():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Jasprit Bumrah",
        professions=["cricketer"],
    )

    priorities = [task.priority for task in plan.tasks]

    assert priorities == sorted(priorities, reverse=True)


def test_task_ids_are_deterministic():
    planner = UniversalResearchPlanner()

    first = planner.build_plan(
        "Example Person",
        professions=["entrepreneur"],
    )

    second = planner.build_plan(
        "Example Person",
        professions=["entrepreneur"],
    )

    assert [task.task_id for task in first.tasks] == [
        task.task_id for task in second.tasks
    ]


def test_aliases_are_included_in_generated_queries():
    planner = UniversalResearchPlanner()

    plan = planner.build_plan(
        "Example Person",
        professions=["entrepreneur"],
        aliases=["Example Founder"],
    )

    assert any(
        "Example Founder" in task.query_text
        for task in plan.tasks
    )