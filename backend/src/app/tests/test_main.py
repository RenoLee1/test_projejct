from types import SimpleNamespace
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.database.session import get_session, Session as SessionTable
from app.models.user_approve import UserApproval
from app.services.auth_service import authenticate_user, register_user
from app.schemas.user_schema import UserRegister
from app.crud.user_crud import get_user_by_id

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from email.message import EmailMessage

import smtplib

from sqlmodel import Session

from app.services import auth_service
from app.services.auth_service import (
    authenticate_user,
    update_or_create_user_session_login_info,
    register_user,
    send_admin_notification,
)
from app.crud.user_crud import update_approval_by_user_id_approve, get_user_by_username
from app.schemas.user_schema import UserRegister
from app.models.user import User

# Testing Database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

@pytest.fixture(scope="session", autouse=True)
def init_db():
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def override_get_session():
    SQLModel.metadata.create_all(engine)
    def _get_session():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = _get_session
    yield
    app.dependency_overrides.clear()

@pytest.fixture()
def client():
    return TestClient(app)

client = TestClient(app)

'''
Tests the registration pipeline using the backend api endpoint.
Calls the client endpoints to register a new user providing the following data fields:
    username, password, first_name, last_name, email, country, affiliation, research.
- Validates that a new user is created, then found, then deleted from the system (returning it to original state)
- If the test passes we can assert that the behaviour of the backend endpoint for registering a user is working according to our team design spec.
'''
def test_user_crud_lifecycle():
    # Test data
    register_data = {
        "username": "testuser123",             # Unique username for login
        "password": "Password123!",            # Plaintext password (passes requirements of security rules)
        "first_name": "Test",                  # User's first name
        "last_name": "User",                   # User's last name
        "email": "testuser123@example.com",    # Contact email
        "role" : "admin",                      # Acc role.
        "status" : "testing",                  # Not a 'valid' value -> to be easy to find and remove if required manually
        "affiliation": "Unimelb",              # Organization or university affiliation
        "research": "Security Research",       # Research topic or area of interest - can't be null.
        "country": "Australia",                # User's country of residence
    }
    # 1. Register user via endpoint
    response = client.post("/register", json=register_data)
    assert response.status_code == 200  # important to check the return code of the api. if not 200, then theres an issue.
    user_id = response.json()["data"]["id"]
    # 2. Lookup the user from DB
    session = next(app.dependency_overrides[get_session]())
    user = get_user_by_id(session, user_id)
    # 3. Confirm user is present
    assert user is not None
    assert user.username == register_data["username"]
    # 4. Delete user
    session.delete(user)
    session.commit()
    # Confirm deletion
    deleted_user = get_user_by_id(session, user_id)
    assert deleted_user is None

def test_register_and_authenticate_user():
    session = next(app.dependency_overrides[get_session]())
    # Generate Info
    user_data = UserRegister(
        username="john",
        password="password123",
        first_name="John",
        last_name="Smith",
        email="johnSmith@example.com",
        country="Australia",
        affiliation="Unimelb",
        research="Research foo"
    )
    # register
    register_user(session, user_data)
    # approve user, pending -> ?
    update_approval_by_user_id_approve(session, get_user_by_username(session, user_data.username).id)
    # check authentication
    (user, _) = authenticate_user(session, "john", "password123")
    assert user is not None
    assert user.username == "john"
    assert user.email == "johnSmith@example.com"

# 1. authenticate_user()
class DummyUser:
    def __init__(self, username, password, id):
        self.username = username
        self.password = password
        self.id = id

def test_authenticate_user_not_found(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: None)
    (result, _) = authenticate_user(db=None, username="noone", password="xxx")
    assert result is None

def test_authenticate_user_wrong_password(monkeypatch):
    dummy = DummyUser("foo", "hashed", 1)
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: dummy)
    monkeypatch.setattr(auth_service, "verify_password", lambda pw, hpw: False)
    (result, _) = authenticate_user(db=None, username="foo", password="wrong")
    assert result is None

def test_authenticate_user_success(monkeypatch):
    dummy = DummyUser("foo", "hashed", 1)
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: dummy)
    monkeypatch.setattr(auth_service, "verify_password", lambda pw, hpw: True)
    monkeypatch.setattr(auth_service, "get_approval_by_user_id", lambda db, i: type('obj', (object,), {'status' : "approved"}))
    (result, _) = authenticate_user(db=None, username="foo", password="correct")
    assert result is dummy

# 2. update_or_create_user_session()
def test_update_or_create_user_session(monkeypatch):
    user = SimpleNamespace(id=1)
    ip = "1.2.3.4"
    called = {}

    # Fake SessionTable result (None to simulate "create" case)
    class FakeResult:
        def first(self):
            return None  # change this to a fake session for "update" case

    # Fake DB session
    class FakeDB:
        def exec(self, statement):
            called["statement"] = statement
            return FakeResult()

        def add(self, obj):
            called["added"] = obj

        def commit(self):
            called["committed"] = True

        def refresh(self, obj):
            called["refreshed"] = obj

    db = FakeDB()

    # Call the function with fakes
    result = update_or_create_user_session_login_info(db=db, user=user, ip=ip)

    # Assertions
    assert result.user_id == user.id
    assert result.login_ip == ip
    assert isinstance(result.login_time, datetime)
    assert called["committed"] is True
    assert called["added"] is result

# 3. register_user()
@pytest.fixture
def dummy_register_data():
    return UserRegister(
        username="alice",
        password="pw123",
        first_name="Alice",
        last_name="Liddell",
        email="alice@example.com",
        country="Wonderland",
        affiliation="TestLab",
        research="Research foo"
    )

def test_register_user_email_conflict(monkeypatch, dummy_register_data):
    # Fake DB session
    class FakeDB:
        def exec(self, statement) -> User:
                class FakeFilterResult:
                    def first(self):
                        return User(
                            id=1,
                            username="intuser",
                            password="hashed_pw",
                            first_name="I",
                            last_name="N",
                            email="i@n.com",
                            role="user",
                            status="active",
                            affiliation="Z",
                            research="research_foo",
                            country="AU",
                            session_id=None
                        )
                return FakeFilterResult()

        def query(self, obj):
            class FakeQuery:
                def filter(self, *args, **kwargs):
                    class FakeFilterResult:
                        def first(self):
                            return None
                    return FakeFilterResult()
            return FakeQuery()

    db = FakeDB()
    with pytest.raises(HTTPException) as exc:
        register_user(db=db, register_data=dummy_register_data)
    assert exc.value.status_code == 400
    assert "Username already registered" in exc.value.detail

def test_register_user_username_conflict(monkeypatch, dummy_register_data):
    dummy_data = UserRegister(
        email="i@n.com",
        username="intuser",  # already taken
        password="pw",
        first_name="I",
        last_name="N",
        affiliation="Z",
        country="Australia",
        research="foo"
    )

    # Simulate that username already exists
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: SimpleNamespace(id=99))
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda db, e: None)  # Email doesn't exist

    with pytest.raises(HTTPException) as exc:
        register_user(db="db", register_data=dummy_data)

    assert exc.value.status_code == 400
    assert "Username already registered" in exc.value.detail

def test_register_user_success(monkeypatch):
    class FakeDB:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass

    # --- Dummy input ---
    dummy_register_data = UserRegister(
        username='alice',
        password='pw123',
        first_name='Alice',
        last_name='Liddell',
        email='alice@example.com',
        country='Wonderland',
        affiliation='TestLab',
        research='Research foo'
    )

    # --- Mock return values ---
    user_obj = SimpleNamespace(id=1, username=dummy_register_data.username, email=dummy_register_data.email)
    # Simulate get_user_by_email: no existing user with this email
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda db, e: None)
    call_state = {"first": True}
    def get_user_by_username_mock(db, username):
        if call_state["first"]:
            call_state["first"] = False
            return None
        return user_obj
    monkeypatch.setattr(auth_service, "get_user_by_username", get_user_by_username_mock)
    # Track whether create_user and send_admin_notification were called
    called = {"create": False, "notify": False}
    monkeypatch.setattr(auth_service, "create_user", lambda **kwargs: called.update(create=True))
    monkeypatch.setattr(auth_service, "send_admin_notification", lambda email, username: called.update(notify=True))

    register_user(db=FakeDB(), register_data=dummy_register_data)
    assert called["create"] is True
    assert called["notify"] is True


# 4. send_admin_notification()
import logging
class DummySMTPSuccess:
    def __init__(self, host, port): pass
    def set_debuglevel(self, lvl): pass
    def login(self, user, pwd):
        return None
    def send_message(self, msg: EmailMessage): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False

#  DummySMTPFail for failure
class DummySMTPFail:
    def __init__(self, host, port): pass
    def set_debuglevel(self, lvl): pass
    def login(self, user, pwd):

        raise Exception("auth failed")
    def send_message(self, msg: EmailMessage): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False


def test_send_admin_notification_success(monkeypatch, caplog):

    monkeypatch.setattr(smtplib, "SMTP_SSL", DummySMTPSuccess)
    caplog.set_level(logging.INFO)

    send_admin_notification(user_email="e@x.com", username="u")

    assert "Email successfully sent to admin." in caplog.text


def test_send_admin_notification_failure(monkeypatch, caplog):

    monkeypatch.setattr(smtplib, "SMTP_SSL", DummySMTPFail)
    caplog.set_level(logging.ERROR)

    send_admin_notification(user_email="e@x.com", username="anyone")

    assert "Failed to send email" in caplog.text

# 5. auth_util.verify_password & get_password_hash

from app.utils.auth_util import verify_password, get_password_hash

def test_verify_password():
    assert verify_password("abc", "abc") is True
    assert verify_password("a", "b") is False

def test_get_password_hash():
    hashed = get_password_hash("mypw")
    assert isinstance(hashed, str)
    assert hashed != "mypw"