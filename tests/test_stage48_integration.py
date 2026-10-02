from dataclasses import dataclass

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.research_job import ResearchJob
from backend.app.services.research_api import ResearchAPIService
from engine.research.orchestration.orchestrator import (
    RegisteredStage,
    ResearchOrchestrator,
)


@dataclass
class StageArtifact:
    name: str
    value: str


def build_deterministic_stages():
    """
    Build a complete deterministic version of the PERSONA-X pipeline.

    External web research is intentionally replaced by deterministic
    artifacts here. The purpose of this test is to validate orchestration,
    lifecycle, persistence boundaries, ordering, and failure behavior
    without making the test suite dependent on an external API.
    """

    def identity(context):
        context.identity = {
            "query_name": context.person_name,
            "canonical_name": context.person_name,
            "status": "resolved",
            "confidence": 1.0,
        }
        return context.identity

    def planning(context):
        context.research_plan = {
            "person_name": context.person_name,
            "tasks": [
                "identity",
                "biography",
                "career",
                "statements",
                "initiatives",
                "achievements",
            ],
        }
        return context.research_plan

    def research(context):
        context.research_results = [
            {
                "title": f"{context.person_name} official biography",
                "url": "https://example.org/person",
                "discovery_method": "deterministic_test",
            },
            {
                "title": f"{context.person_name} career record",
                "url": "https://example.org/career",
                "discovery_method": "deterministic_test",
            },
        ]
        return context.research_results

    def source_processing(context):
        context.sources = [
            {
                "id": 1,
                "url": "https://example.org/person",
                "verified": True,
            },
            {
                "id": 2,
                "url": "https://example.org/career",
                "verified": True,
            },
        ]
        return context.sources

    def extraction(context):
        context.evidence = [
            {
                "id": 101,
                "source_id": 1,
                "text": f"{context.person_name} has a documented career.",
                "confidence": 1.0,
            },
            {
                "id": 102,
                "source_id": 2,
                "text": f"{context.person_name} has documented professional activity.",
                "confidence": 1.0,
            },
        ]

        context.claims = [
            {
                "id": 201,
                "evidence_id": 101,
                "text": "Documented career",
            }
        ]

        context.statements = [
            {
                "id": 301,
                "evidence_id": 102,
                "text": "Documented public statement",
            }
        ]

        context.timeline_events = [
            {
                "id": 401,
                "evidence_id": 101,
                "title": "Career activity",
            }
        ]

        context.initiatives = [
            {
                "id": 501,
                "evidence_id": 102,
                "name": "Documented initiative",
                "lifecycle_stage": "announced",
            }
        ]

        return {
            "evidence": context.evidence,
            "claims": context.claims,
            "statements": context.statements,
            "timeline_events": context.timeline_events,
            "initiatives": context.initiatives,
        }

    def analysis(context):
        context.topic_view_result = {
            "topics": ["career", "public_activity"],
            "views": [],
        }

        context.temporal_result = {
            "status": "insufficient_evidence",
            "changes": [],
        }

        context.contradiction_result = {
            "comparisons": [],
            "potential_inconsistencies": 0,
        }

        return {
            "topic_view": context.topic_view_result,
            "temporal": context.temporal_result,
            "contradictions": context.contradiction_result,
        }

    def profession(context):
        context.profession_result = {
            "person_name": context.person_name,
            "professions": ["generic"],
            "findings": [
                {
                    "title": "Documented professional activity",
                    "confidence": 1.0,
                }
            ],
            "evidence_count": len(context.evidence),
        }

        return context.profession_result

    def political(context):
        context.political_result = {
            "person_name": context.person_name,
            "applicable": False,
            "sufficient": False,
            "limitations": [
                "No political classification inferred in deterministic integration test."
            ],
        }

        return context.political_result

    def evidence_graph(context):
        context.evidence_graph = {
            "nodes": [
                "person",
                "source",
                "evidence",
                "claim",
                "statement",
                "timeline_event",
                "initiative",
                "profession_finding",
            ],
            "edges": [
                ("person", "evidence"),
                ("evidence", "source"),
                ("evidence", "claim"),
                ("evidence", "statement"),
                ("evidence", "timeline_event"),
                ("evidence", "initiative"),
                ("profession_finding", "evidence"),
            ],
        }

        return context.evidence_graph

    def dossier(context):
        context.dossier = {
            "person_name": context.person_name,
            "title": f"PERSONA-X dossier: {context.person_name}",
            "source_count": len(context.sources),
            "evidence_count": len(context.evidence),
            "political_analysis_included": False,
            "status": "generated",
        }

        return context.dossier

    return [
        RegisteredStage("identity", identity, required=True),
        RegisteredStage("planning", planning, required=True),
        RegisteredStage("research", research, required=True),
        RegisteredStage("source_processing", source_processing, required=True),
        RegisteredStage("extraction", extraction, required=True),
        RegisteredStage("analysis", analysis, required=True),
        RegisteredStage("profession", profession, required=True),
        RegisteredStage("political", political, required=False),
        RegisteredStage("evidence_graph", evidence_graph, required=True),
        RegisteredStage("dossier", dossier, required=True),
    ]


def test_stage48_complete_pipeline():
    orchestrator = ResearchOrchestrator(
        stages=build_deterministic_stages()
    )

    result = orchestrator.run(
        person_name="PERSONA-X Integration Person",
        research_job_id=1001,
    )

    assert result.status == "completed"
    assert result.error is None
    assert result.failed_stages == []

    expected_order = [
        "identity",
        "planning",
        "research",
        "source_processing",
        "extraction",
        "analysis",
        "profession",
        "political",
        "evidence_graph",
        "dossier",
    ]

    assert result.completed_stages == expected_order

    context = result.context

    assert context.identity["status"] == "resolved"
    assert len(context.research_results) == 2
    assert len(context.sources) == 2
    assert len(context.evidence) == 2
    assert len(context.claims) == 1
    assert len(context.statements) == 1
    assert len(context.timeline_events) == 1
    assert len(context.initiatives) == 1

    assert context.profession_result["evidence_count"] == 2
    assert context.political_result["applicable"] is False

    assert "evidence" in context.evidence_graph["nodes"]
    assert "source" in context.evidence_graph["nodes"]
    assert "claim" in context.evidence_graph["nodes"]

    assert context.dossier["status"] == "generated"
    assert context.dossier["evidence_count"] == 2


def test_stage48_optional_failure_continues_pipeline():
    stages = build_deterministic_stages()

    original_political = stages[7].handler

    def failing_political(context):
        raise RuntimeError("intentional optional political failure")

    stages[7] = RegisteredStage(
        name="political",
        handler=failing_political,
        required=False,
    )

    orchestrator = ResearchOrchestrator(stages=stages)

    result = orchestrator.run(
        person_name="Optional Failure Person"
    )

    assert result.status == "failed"
    assert result.failed_stages == ["political"]

    assert "evidence_graph" in result.completed_stages
    assert "dossier" in result.completed_stages

    political_stage = next(
        item
        for item in result.context.stages
        if item.stage == "political"
    )

    assert political_stage.status == "failed"
    assert "intentional optional political failure" in (
        political_stage.message or ""
    )

    assert original_political is not None


def test_stage48_required_failure_stops_pipeline():
    stages = build_deterministic_stages()

    def failing_extraction(context):
        raise RuntimeError("intentional required extraction failure")

    stages[4] = RegisteredStage(
        name="extraction",
        handler=failing_extraction,
        required=True,
    )

    orchestrator = ResearchOrchestrator(stages=stages)

    result = orchestrator.run(
        person_name="Required Failure Person"
    )

    assert result.status == "failed"
    assert result.failed_stages == ["extraction"]

    assert "identity" in result.completed_stages
    assert "planning" in result.completed_stages
    assert "research" in result.completed_stages
    assert "source_processing" in result.completed_stages

    assert "analysis" not in result.completed_stages
    assert "profession" not in result.completed_stages
    assert "dossier" not in result.completed_stages


def test_stage48_api_creates_persistent_research_job():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research",
            json={
                "person_name": "Stage 48 API Person",
                "requested_scope": {
                    "integration_test": True
                },
            },
        )

    assert response.status_code == 201

    payload = response.json()

    assert payload["job_id"] is not None
    assert payload["person_id"] is not None
    assert payload["person_name"] == "Stage 48 API Person"
    assert payload["status"] == "queued"
    assert payload["current_stage"] == "queued"

    db = SessionLocal()

    try:
        job = (
            db.query(ResearchJob)
            .filter(ResearchJob.id == payload["job_id"])
            .first()
        )

        assert job is not None
        assert job.status == "queued"
        assert job.current_stage == "queued"
        assert job.requested_scope == {
            "integration_test": True
        }

        person = ResearchAPIService.get_person_for_job(
            db=db,
            job=job,
        )

        assert person is not None
        assert person.canonical_name == "Stage 48 API Person"

    finally:
        db.close()


def test_stage48_api_status_round_trip():
    with TestClient(app) as client:
        create_response = client.post(
            "/api/v1/research",
            json={
                "person_name": "Stage 48 Status Person"
            },
        )

        assert create_response.status_code == 201

        job_id = create_response.json()["job_id"]

        status_response = client.get(
            f"/api/v1/research/{job_id}"
        )

    assert status_response.status_code == 200

    payload = status_response.json()

    assert payload["job_id"] == job_id
    assert payload["person_name"] == "Stage 48 Status Person"
    assert payload["status"] == "queued"
    assert payload["query_count"] == 0
    assert payload["source_count"] == 0
    assert payload["evidence_count"] == 0