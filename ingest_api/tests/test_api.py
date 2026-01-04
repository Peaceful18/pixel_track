import json

import pytest

from app_config.config import settings


@pytest.mark.asyncio
async def test_track_endpoint_integration(redis_client, async_client):
    test_event = {
        "event": "test_ci",
        "type": "http",  # Тип http вимагає наявності raw_log
        "service": "test_service",
        "source": "pytest",
        "user_id": "user_1",
        "timestamp": "2026-01-04T12:00:00Z",
        "payload": {
            "raw_log": "GET /api/v1/resource HTTP/1.1 200 OK",  # Тепер валідатор пропустить!
            "request_id": "123",
        },
    }

    response = await async_client.post("/ingest/track", json=test_event)

    assert response.status_code == 202

    # Перевіряємо дані в Redis
    raw_data = await redis_client.rpop(settings.REDIS_QUEUE_KEY)
    assert raw_data is not None
    data = json.loads(raw_data)
    assert data["event"] == "test_ci"
