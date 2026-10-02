from engine.research.orchestration import (
    RegisteredStage,
    ResearchOrchestrationService,
    ResearchOrchestrator,
)


def test_orchestrator_runs_registered_stages_in_order():
    executed = []

    def identity(context):
        executed.append("identity")
        context.identity = {"canonical_name": context.person_name}
        return context.identity

    def planning(context):
        executed.append("planning")
        context.research_plan = {"queries": 3}
        return context.research_plan

    orchestrator = ResearchOrchestrator(
        stages=[
            RegisteredStage("identity", identity),
            RegisteredStage("planning", planning),
        ]
    )

    result = orchestrator.run("Jasprit Bumrah")

    assert result.status == "completed"
    assert result.error is None
    assert executed == ["identity", "planning"]
    assert result.completed_stages == [
        "identity",
        "planning",
    ]


def test_orchestrator_preserves_shared_context():
    def identity(context):
        context.identity = {
            "canonical_name": "Jasprit Bumrah",
        }
        return context.identity

    def planning(context):
        assert context.identity["canonical_name"] == "Jasprit Bumrah"
        context.research_plan = {
            "task_count": 10,
        }
        return context.research_plan

    service = ResearchOrchestrationService(
        stages=[
            RegisteredStage("identity", identity),
            RegisteredStage("planning", planning),
        ]
    )

    result = service.run("Jasprit Bumrah")

    assert result.status == "completed"
    assert result.context.identity["canonical_name"] == (
        "Jasprit Bumrah"
    )
    assert result.context.research_plan["task_count"] == 10


def test_required_stage_failure_stops_pipeline():
    executed = []

    def identity(context):
        executed.append("identity")
        raise RuntimeError("identity failed")

    def planning(context):
        executed.append("planning")

    orchestrator = ResearchOrchestrator(
        stages=[
            RegisteredStage("identity", identity),
            RegisteredStage("planning", planning),
        ]
    )

    result = orchestrator.run("Unknown Person")

    assert result.status == "failed"
    assert result.failed_stages == ["identity"]
    assert result.completed_stages == []
    assert executed == ["identity"]
    assert "identity failed" in result.error


def test_optional_stage_failure_continues_pipeline():
    executed = []

    def identity(context):
        executed.append("identity")

    def political(context):
        executed.append("political")
        raise RuntimeError("political analysis unavailable")

    def dossier(context):
        executed.append("dossier")
        context.dossier = {"status": "built"}

    orchestrator = ResearchOrchestrator(
        stages=[
            RegisteredStage("identity", identity),
            RegisteredStage(
                "political",
                political,
                required=False,
            ),
            RegisteredStage("dossier", dossier),
        ]
    )

    result = orchestrator.run("Example Person")

    assert result.status == "failed"
    assert result.failed_stages == ["political"]

    assert executed == [
        "identity",
        "political",
        "dossier",
    ]

    assert "dossier" in result.completed_stages
    assert result.context.dossier["status"] == "built"


def test_empty_person_name_is_rejected():
    orchestrator = ResearchOrchestrator()

    try:
        orchestrator.run("   ")
    except ValueError as exc:
        assert "person_name" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for empty person name."
        )


def test_stage_registration_requires_callable():
    orchestrator = ResearchOrchestrator()

    try:
        orchestrator.register(
            "identity",
            "not callable",
        )
    except TypeError as exc:
        assert "callable" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError for non-callable handler."
        )


def test_registered_stage_order_matches_pipeline_order():
    def handler(context):
        return None

    orchestrator = ResearchOrchestrator(
        stages=[
            RegisteredStage("dossier", handler),
            RegisteredStage("identity", handler),
            RegisteredStage("research", handler),
            RegisteredStage("planning", handler),
        ]
    )

    assert orchestrator.registered_stages() == [
        "identity",
        "planning",
        "research",
        "dossier",
    ]