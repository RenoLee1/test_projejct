# tests/test_crud_csv_files.py

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

# Insert path to src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app as fastapi_app
from app.database.session import get_session
from app.crud import csv_files_crud
from app.models.csv_files import CSVFile
from app.models.job import Job
from app.models.session import Session as SessionTable
from app.models.results import Results
from app.models.job_metrics import JobMetrics
from app.models.problem import Problem

# Setup in-memory database
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
    yield
    fastapi_app.dependency_overrides.clear()

@pytest.fixture
def db_session():
    with Session(engine) as session:
        yield session

@pytest.fixture
def create_job(db_session):
    job = Job(
        problem_id=1,
        status="created",
        user_id=1
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job

# ---------------------- TESTS ----------------------

def create_sample_csv(db_session):
    csv = csv_files_crud.create_csv(
        db_session,
        filename="test.csv",
        content="header1,header2\nval1,val2"
    )
    return csv


def test_create_csv(db_session, create_job):
    new_csv = csv_files_crud.create_csv(
        db=db_session,
        filename="sample.csv",
        content="a,b\n1,2"
    )
    assert new_csv.filename == "sample.csv"


def test_get_csv_found(db_session, create_job):
    sample_csv = create_sample_csv(db_session)
    fetched_csv = csv_files_crud.get_csv(db_session, id=sample_csv.id)
    assert fetched_csv is not None
    assert fetched_csv.filename == "test.csv"


def test_get_csv_not_found(db_session):
    csv = csv_files_crud.get_csv(db_session, id=9999)
    assert csv is None


def test_delete_csv_success(db_session):
    sample_csv = create_sample_csv(db_session)
    result = csv_files_crud.delete_csv(db_session, id=sample_csv.id)
    assert result is True

    deleted_csv = csv_files_crud.get_csv(db_session, id=sample_csv.id)
    assert deleted_csv is None


def test_delete_csv_failure(db_session):
    result = csv_files_crud.delete_csv(db_session, id=9999)
    assert result is False
