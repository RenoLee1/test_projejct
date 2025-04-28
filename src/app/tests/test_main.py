import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.database.session import get_session
from app.services.auth_service import authenticate_user, register_user
from app.schemas.user_schema import UserRegister

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from email.message import EmailMessage

import smtplib

from sqlmodel import Session

from app.services import auth_service
from app.services.auth_service import (
    authenticate_user,
    update_user_login_info,
    register_user,
    send_admin_notification,
)
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


# 二、Unit Test

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
        research=None
    )
    # register
    register_user(session, user_data)
    # check authentication
    user = authenticate_user(session, "john", "password123")
    assert user is not None
    assert user.username == "john"
    assert user.email == "johnSmith@example.com"

# 1. authenticate_user()
class DummyUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password

def test_authenticate_user_not_found(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: None)
    result = authenticate_user(db=None, username="noone", password="xxx")
    assert result is None

def test_authenticate_user_wrong_password(monkeypatch):
    dummy = DummyUser("foo", "hashed")
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: dummy)
    monkeypatch.setattr(auth_service, "verify_password", lambda pw, hpw: False)
    result = authenticate_user(db=None, username="foo", password="wrong")
    assert result is None

def test_authenticate_user_success(monkeypatch):
    dummy = DummyUser("foo", "hashed")
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: dummy)
    monkeypatch.setattr(auth_service, "verify_password", lambda pw, hpw: True)
    result = authenticate_user(db=None, username="foo", password="correct")
    assert result is dummy

# 2. update_user_login_info()
def test_update_user_login_info(monkeypatch):
    user = User(
        id=1,
        username="bob",
        password="pw",
        first_name="Bob",
        last_name="Builder",
        email="bob@example.com",
        country="Nowhere",
        affiliation="Test",
        status="active",
        role="user",
    )
    called = {}
    def fake_update(db, u):
        called['user'] = u
        return u
    monkeypatch.setattr(auth_service, "update_user", fake_update)
    returned = update_user_login_info(db="db", user=user, ip="1.2.3.4")

    assert isinstance(returned.login_time, datetime)
    assert returned.login_time > datetime.now() - timedelta(seconds=1)
    assert returned.login_ip == "1.2.3.4"
    assert called['user'] is user
    assert returned is user

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
        research=None
    )

def test_register_user_email_conflict(monkeypatch, dummy_register_data):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda db, e: True)
    with pytest.raises(HTTPException) as exc:
        register_user(db="db", register_data=dummy_register_data)
    assert exc.value.status_code == 400
    assert "Email already registered" in exc.value.detail

def test_register_user_username_conflict(monkeypatch, dummy_register_data):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda db, e: None)
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: True)
    with pytest.raises(HTTPException) as exc:
        register_user(db="db", register_data=dummy_register_data)
    assert exc.value.status_code == 400
    assert "username already registered" in exc.value.detail

def test_register_user_success(monkeypatch, dummy_register_data):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda db, e: None)
    monkeypatch.setattr(auth_service, "get_user_by_username", lambda db, u: None)

    called = {"create": False, "notify": False}
    monkeypatch.setattr(auth_service, "create_user", lambda **kwargs: called.update(create=True))
    monkeypatch.setattr(auth_service, "send_admin_notification", lambda em, un: called.update(notify=True))

    register_user(db="db", register_data=dummy_register_data)

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
        # 无论传什么都抛异常
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