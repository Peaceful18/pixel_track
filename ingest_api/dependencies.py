from typing import AsyncGenerator

from redis.asyncio import Redis

from infra.redis_provider import redis_provider


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Адаптер для FastAPI Depends.
    Він бере контекстний менеджер з провайдера і перетворює його на генератор,
    який розуміє FastAPI.
    """
    async with redis_provider.get_client() as client:
        yield client
