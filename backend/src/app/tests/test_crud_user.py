# tests/test_crud_user.py

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
from app.crud import user_crud
from app.models.user import User

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

def test_create_user(db_session):
    user = user_crud.create_user(
        db_session,
        username="testuser",
        password="password123",
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        country="AU",
        affiliation="Test University",
        research="research foo"
    )
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"


def test_get_user_by_username_found(db_session):
    user = user_crud.get_user_by_username(db_session, username="testuser")
    assert user is not None
    assert user.username == "testuser"


def test_get_user_by_username_not_found(db_session):
    user = user_crud.get_user_by_username(db_session, username="nonexistent")
    assert user is None


def test_get_user_by_email_found(db_session):
    user = user_crud.get_user_by_email(db_session, email="testuser@example.com")
    assert user is not None
    assert user.email == "testuser@example.com"


def test_get_user_by_email_not_found(db_session):
    user = user_crud.get_user_by_email(db_session, email="noemail@example.com")
    assert user is None


def test_get_user_by_id_found(db_session):
    created_user = user_crud.get_user_by_username(db_session, username="testuser")
    user = user_crud.get_user_by_id(db_session, user_id=created_user.id)
    assert user is not None
    assert user.username == "testuser"


def test_get_user_by_id_not_found(db_session):
    user = user_crud.get_user_by_id(db_session, user_id=9999)
    assert user is None


def test_update_user(db_session):
    user = user_crud.get_user_by_username(db_session, username="testuser")
    user.last_name = "NewLastName"
    updated_user = user_crud.update_user(db_session, user)
    assert updated_user.last_name == "NewLastName"


