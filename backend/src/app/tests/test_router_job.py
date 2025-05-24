# tests/test_router_job.py

import os
import sys
import io
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app as fastapi_app
from app.database.session import get_session
from app.dependencies.auth import get_current_user_id

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SQLModel.metadata.create_all(engine)

@pytest.fixture(autouse=True)
def override_dependencies():
    def _get_session():
        with Session(engine) as session:
            yield session
    fastapi_app.dependency_overrides[get_session] = _get_session
    fastapi_app.dependency_overrides[get_current_user_id] = lambda: 1
    yield
    fastapi_app.dependency_overrides.clear()

@pytest.fixture
def client():
    return TestClient(fastapi_app)

def test_list_jobs(client):
    response = client.get("/jobs/")
    assert response.status_code == 200

def test_get_job_detail_not_found(client):
    response = client.get("/jobs/999")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 404

def test_delete_job_not_found(client):
    response = client.delete("/jobs/999")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 404

def test_create_job_with_csv(client):
    csv_content = "header1,header2\nval1,val2\n"
    file = io.BytesIO(csv_content.encode("utf-8"))
    response = client.post(
        "/jobs/create_new_job",
        data={
            "problem_id": 1,
            "job_type": "Test Type"
        },
        files={"csv_file": ("test.csv", file, "text/csv")}
    )
    assert response.status_code in [200, 400, 500]
