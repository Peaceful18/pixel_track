from redis import asyncio as aioredis

from infra.redis_provider import redis_provider


async def get_redis_client():
    """
    Асинхронне створення клієнта Redis
    """
    if redis_provider.pool is None:
        redis_provider.init_pool()
    pool = redis_provider.pool
    client = aioredis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.aclose()
