import asyncio

import pytest
from redis.asyncio import Redis

from app_config.config import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def redis_client():
    """
    Фікстура для клієнта Redis.
    Саме її шукає твій тест під ім'ям 'client'.
    """
    # Підключаємося до Redis (у CI це буде localhost:6379)
    redis = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )

    # Даємо клієнт тесту
    yield redis

    # Очищуємо базу після тесту, щоб наступні тести були в "чистому" середовищі
    await redis.flushdb()
    await redis.close()
