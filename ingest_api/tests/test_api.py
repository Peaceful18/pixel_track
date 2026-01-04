import json

import pytest
from httpx import ASGITransport, AsyncClient

from app_config.config import settings
from ingest_api.main import app


@pytest.mark.asyncio
async def test_track_endpoint_integration(redis_client):
    test_event = {
        "event": "test_ci",
        "type": "custom",
        "service": "test_service",
        "source": "pytest",
        "user_id": "user_1",
        "timestamp": "2026-01-04T12:00:00Z",
        "payload": {"key": "value"},
    }

    # Створюємо транспорт для FastAPI
    transport = ASGITransport(app=app)

    # Передаємо transport замість app
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/ingest/track", json=test_event)

    assert response.status_code == 202

    # Перевіряємо дані в Redis
    raw_data = await redis_client.rpop(settings.REDIS_QUEUE_KEY)
    assert raw_data is not None
    data = json.loads(raw_data)
    assert data["event"] == "test_ci"
