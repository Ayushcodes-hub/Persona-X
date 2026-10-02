import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.person import Person
from backend.app.models.timeline import TimelineEvent
from backend.app.models.statement import Statement
from backend.app.models.evidence import Evidence
from backend.app.models.source import Source

client = TestClient(app)


@pytest.fixture
def sample_person_with_data():
    db = SessionLocal()
    try:
        # Create person
        person = Person(
            canonical_name="Dr. Eleanor Vance",
            primary_profession="Astrophysicist",
            identity_status="resolved",
            identity_confidence=0.98,
            aliases="E. Vance",
        )
        db.add(person)
        db.commit()
        db.refresh(person)

        # Create source
        source = Source(
            url="https://example.org/eleanor-vance-discovery",
            publisher="example.org",
            source_type="article",
            title="Discovery of Exoplanet Kepler-186f",
            source_tier=1,
            reliability_score=0.95,
        )
        db.add(source)
        db.commit()
        db.refresh(source)

        # Create evidence
        evidence = Evidence(
            person_id=person.id,
            source_id=source.id,
            evidence_type="scientific_publication",
            extracted_text="Dr. Vance led the research team discovering atmospheric water vapor.",
            confidence=0.96,
            verification_status="verified",
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        # Create timeline event
        event = TimelineEvent(
            person_id=person.id,
            evidence_id=evidence.id,
            event_type="career_milestone",
            title="Appointed Lead Researcher at Kepler Institute",
            start_date=datetime(2020, 5, 1, tzinfo=timezone.utc),
            confidence=0.95,
        )
        db.add(event)

        # Create statement
        statement = Statement(
            person_id=person.id,
            source_id=source.id,
            evidence_id=evidence.id,
            statement_type="interview",
            text="Space exploration must be an open, globally collaborative endeavor funded by public-private coalitions.",
            topic="Space Policy",
            confidence=0.92,
            attribution_status="attributed",
        )
        db.add(statement)

        db.commit()

        yield person.id

        # Cleanup
        db.query(Statement).filter(Statement.person_id == person.id).delete()
        db.query(TimelineEvent).filter(TimelineEvent.person_id == person.id).delete()
        db.query(Evidence).filter(Evidence.person_id == person.id).delete()
        db.query(Source).filter(Source.id == source.id).delete()
        db.query(Person).filter(Person.id == person.id).delete()
        db.commit()
    finally:
        db.close()


def test_system_status():
    res = client.get("/api/v1/system/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "uptime_seconds" in data
    assert "ai" in data
    assert "worker" in data


def test_system_metrics():
    res = client.get("/api/v1/system/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "platform" in data
    assert "ai_accounting" in data
    assert "total_persons" in data["platform"]


def test_person_endpoints(sample_person_with_data):
    person_id = sample_person_with_data

    # 1. Search
    search_res = client.get("/api/v1/persons/search?q=Eleanor&include_external=false")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["local_count"] >= 1
    assert any(p["id"] == person_id for p in search_data["local_persons"])

    # 2. Get profile
    profile_res = client.get(f"/api/v1/persons/{person_id}")
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["canonical_name"] == "Dr. Eleanor Vance"
    assert profile_data["primary_profession"] == "Astrophysicist"
    assert profile_data["counts"]["evidence"] >= 1

    # 3. Timeline
    timeline_res = client.get(f"/api/v1/persons/{person_id}/timeline")
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert timeline_data["count"] >= 1
    assert timeline_data["events"][0]["title"] == "Appointed Lead Researcher at Kepler Institute"

    # 4. Statements
    stmt_res = client.get(f"/api/v1/persons/{person_id}/statements")
    assert stmt_res.status_code == 200
    stmt_data = stmt_res.json()
    assert stmt_data["count"] >= 1

    # 5. Evidence Graph
    graph_res = client.get(f"/api/v1/persons/{person_id}/graph")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert graph_data["node_count"] >= 3
    assert graph_data["edge_count"] >= 2
    types = {n["type"] for n in graph_data["nodes"]}
    assert "person" in types
    assert "evidence" in types

    # 6. Political Analysis (non-political figure should return non-applicable with explicit lack of evidence notification)
    pol_res = client.get(f"/api/v1/persons/{person_id}/analysis/political")
    assert pol_res.status_code == 200
    pol_data = pol_res.json()
    assert "applicable" in pol_data
    assert "sufficiency" in pol_data
