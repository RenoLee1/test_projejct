# tests/test_crud_job.py

from datetime import datetime, timezone
import os
import sys
import io
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from app.models.csv_files import CSVFile

# Insert path to src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app as fastapi_app
from app.database.session import get_session
from app.crud import job_crud
from app.models.job import Job

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

# ---------------------- TESTS ----------------------

def create_sample_job(db_session):
    job = Job(
        user_id=1,
        problem_id=1,
        job_status="pending"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


def test_create_job_with_csv(db_session):
    with patch("app.crud.job_crud.create_csv") as mock_create_csv:
        mock_create_csv.return_value = CSVFile(
            id=123,
            filename="test.csv",
            file_content="col1,col2\nval1,val2",
            file_size=25,
            upload_time=datetime.now(timezone.utc),
            checksum="fake-checksum"
        )

        job_data = {
            "problem_id": 1
        }
        csv_bytes = io.BytesIO(b"col1,col2\nval1,val2\n")
        mock_file = StarletteUploadFile(filename="test.csv", file=csv_bytes)

        job = job_crud.create_job_with_csv(
            db=db_session,
            job_data=job_data,
            user_id=1,
            csv_content=mock_file
        )

        assert job.problem_id == 1


def test_get_job_found(db_session):
    sample_job = create_sample_job(db_session)
    fetched_job = job_crud.get_job(db_session, id=sample_job.id)
    assert fetched_job is not None
    assert fetched_job.id == sample_job.id


def test_get_job_not_found(db_session):
    job = job_crud.get_job(db_session, id=9999)
    assert job is None


def test_get_jobs_by_user(db_session):
    create_sample_job(db_session)
    jobs = job_crud.get_jobs_by_user(db_session, user_id=1)
    assert isinstance(jobs, list)
    assert len(jobs) >= 1


def test_get_job_with_csv_found(db_session):
    sample_job = create_sample_job(db_session)
    fetched_job = job_crud.get_job_with_csv(db_session, job_id=sample_job.id, user_id=1)
    assert fetched_job is not None
    assert fetched_job.id == sample_job.id


def test_get_job_with_csv_not_found(db_session):
    job = job_crud.get_job_with_csv(db_session, job_id=9999, user_id=1)
    assert job is None


def test_delete_job(db_session):
    with patch("app.crud.job_crud.delete_csv") as mock_delete_csv:
        mock_delete_csv.return_value = None

        sample_job = create_sample_job(db_session)
        result = job_crud.delete_job(db_session, id=sample_job.id)
        assert result is True

        # Verify deletion
        deleted_job = job_crud.get_job(db_session, id=sample_job.id)
        assert deleted_job is None
