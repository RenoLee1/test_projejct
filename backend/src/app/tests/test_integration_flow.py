# tests/test_integration_flow.py

import pytest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.crud.user_crud import update_approval_by_user_id_approve, get_user_by_username
from app.main import app as fastapi_app
from app.database.session import get_session

import app.models.user  # noqa
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel import Session

TEST_DB_URL = "sqlite:///:memory:"

# Using StaticPool let all conversation point into one database
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(scope="session", autouse=True)
def init_db():
    # Create table
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def override_get_session():
    def _get_session():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_session] = _get_session
    yield
    fastapi_app.dependency_overrides.clear()

from app.services import password_reset as prs
@pytest.fixture(autouse=True)
def fix_verification_code(monkeypatch):
    monkeypatch.setattr(prs, "generate_code", lambda: "1234")
@pytest.fixture(scope="module")
def client():
    return TestClient(fastapi_app)

def test_full_user_flow(client):
    # 1. Register
    r = client.post("/api/auth/register", json={
        "username":"intuser",
        "password":"pw",
        "first_name":"I",
        "last_name":"N",
        "email":"i@n.com",
        "country":"AU",
        "affiliation":"Z",
        "research":"research_foo"
    })
    assert r.status_code == 200
    assert r.json().get("code") == 200

    # approve the user after they are registered
    a_json = {
        "user_id": r.json()["data"],
        "status": "approved",
        "reviewer": "admin",
        "version": 1
    }
    r = client.post("/api/auth/approve", json=a_json)
    assert r.status_code == 200
    assert r.json().get("code") == 200

    # Login
    r = client.post("/api/auth/login", json={
        "username":"intuser",
        "password":"pw"
    })
    assert r.status_code == 200
    j = r.json()
    assert j["code"] == 200
    assert j["data"]["username"] == "intuser"
    assert "session" in r.cookies

    # Forget Password
    r = client.post("/api/password/forgot-password", json={"email":"i@n.com"})
    assert r.status_code == 200
    assert r.json() is True

    r = client.post("/api/password/send-code", json={"email":"i@n.com"})
    assert r.status_code == 200
    assert r.json()["msg"].startswith("Verification code")

    r = client.post(
        "/api/password/verify-code",
        json={"email":"i@n.com", "code":"1234"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["msg"] == "Code verified"
    token = body["token"]

    # Reset Password
    r = client.post("/api/password/reset-password", json={
        "token": token,
        "new_password": "newpw",
    })
    assert r.status_code == 200
    assert r.json().get("msg") == "Password reset successful"


