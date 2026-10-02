import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.user import User

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_users():
    db = SessionLocal()
    try:
        db.query(User).filter(User.username.like("testuser_%")).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def test_auth_signup_and_login():
    username = "testuser_alpha"
    email = "testuser_alpha@example.com"
    password = "SuperSecretPassword123!"

    # 1. Sign up
    signup_res = client.post("/api/v1/auth/signup", json={
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test Alpha",
    })
    assert signup_res.status_code == 201
    data = signup_res.json()
    assert "access_token" in data
    assert data["username"] == username
    token = data["access_token"]

    # 2. Get /me with token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == username
    assert me_data["email"] == email

    # 3. Log in
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": email,
        "password": password,
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data


def test_auth_duplicate_rejected():
    username = "testuser_beta"
    email = "testuser_beta@example.com"
    password = "SuperSecretPassword123!"

    res1 = client.post("/api/v1/auth/signup", json={
        "username": username,
        "email": email,
        "password": password,
    })
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/signup", json={
        "username": username,
        "email": "different@example.com",
        "password": password,
    })
    assert res2.status_code == 409
