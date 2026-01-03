from redis import RedisError
from redis import asyncio as aioredis

from app_config.config import settings


async def brpop_event(client: aioredis.Redis) -> str:
    """
    Використовуємо BRPOP (Blocking Right Pop),
    тоді воркер робитиме LPOP.
    """
    try:
        return await client.brpop(settings.REDIS_QUEUE_KEY, timeout=2)
    except RedisError as e:
        print(f"Redis error: {e}")
        return None
