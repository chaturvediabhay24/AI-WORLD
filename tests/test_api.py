import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "AI World"


@pytest.mark.asyncio
async def test_create_provider(db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/providers/",
            json={
                "name": "openai",
                "api_key": "test-key",
                "config": {
                    "model_name": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "openai"
    assert "api_key" in data
    assert data["config"]["model_name"] == "gpt-3.5-turbo"


@pytest.mark.asyncio
async def test_list_providers(test_provider, db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/providers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["name"] == "test_openai" for p in data)


@pytest.mark.asyncio
async def test_chat(test_provider, db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/chat",
            json={
                "message": "Hello, how are you?",
                "model_provider_id": test_provider.id,
                "stream": False
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert data["user_message"] == "Hello, how are you?"
    assert "assistant_message" in data
    assert data["model_provider"]["name"] == "test_openai"


@pytest.mark.asyncio
async def test_chat_history(test_provider, test_chat_history, db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/chat/history/{test_provider.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["user_message"] == "Hello"
    assert data[0]["assistant_message"] == "Hi there!"


@pytest.mark.asyncio
async def test_delete_provider(test_provider, db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/providers/{test_provider.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Provider deleted successfully"

    # Verify provider is deleted
    response = await ac.get(f"/api/v1/providers/{test_provider.id}")
    assert response.status_code == 404
