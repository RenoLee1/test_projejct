# tests/test_router_log.py

import os
import sys
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app as fastapi_app

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SQLModel.metadata.create_all(engine)

@pytest.fixture
def client():
    return TestClient(fastapi_app)

@pytest.mark.asyncio
async def test_download_matilda_log(client):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.iter_bytes = lambda: iter([b"log content"])

        response = client.get("/log/?file_url=http://example.com/log.txt")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_matilda_log(client):
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "sample log content"

        response = client.get("/log/get-matilda-log?file_url=http://example.com/log.txt")
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
