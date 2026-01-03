from redis import RedisError
from redis import asyncio as aioredis

from app_config.config import settings


async def push_event(event_json: str, client: aioredis.Redis) -> None:
    """
    Проста операція O(1) для вставки в кінець списку (LPUSH/RPUSH).
    Використовуємо LPUSH (Left Push), тоді воркер робитиме RPOP.
    """
    try:
        await client.lpush(settings.REDIS_QUEUE_KEY, event_json)
    except RedisError as e:
        print(f"Redis error: {e}")
        raise e


async def push_event_batch(events_json: list[str], client: aioredis.Redis) -> None:
    """
    Використовує pipeline для масової вставки[cite: 501].
    Зменшує кількість RTT (Round Trip Time).
    """
    try:
        pipe = client.pipeline()
        for event in events_json:
            pipe.lpush(settings.REDIS_QUEUE_KEY, event)
        await pipe.execute()
    except RedisError as e:
        print(f"Redis error: {e}")
        raise e


async def check_health(client: aioredis.Redis) -> bool:
    """
    Перевірка з'єднання [cite: 509]
    """
    try:
        return await client.ping()
    except RedisError:
        return False
