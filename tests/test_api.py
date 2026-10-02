from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "PERSONA-X"
    assert data["status"] == "online"
    assert data["api"] == "/api/v1"


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "PERSONA-X"


def test_research_missing_job_returns_404():
    response = client.get("/api/v1/research/999999999")

    assert response.status_code == 404

    data = response.json()

    assert "not found" in data["detail"]


def test_dossier_missing_id_returns_404():
    response = client.get("/api/v1/dossiers/999999999")

    assert response.status_code == 404

    data = response.json()

    assert "not found" in data["detail"]