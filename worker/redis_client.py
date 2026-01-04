from redis import RedisError
from redis import asyncio as aioredis

from app_config.config import settings


async def get_event_reliable(client: aioredis.Redis) -> str:
    """
    Використовуємо BRPOP (Blocking Right Pop),
    тоді воркер робитиме LPOP.
    """
    try:
        return await client.blmove(
            settings.REDIS_QUEUE_KEY,
            settings.REDIS_PROCESSING_KEY,
            timeout=2,
            src="right",
            dest="left",
        )
    except RedisError as e:
        print(f"Redis error: {e}")
        return None


async def ack_event_processed(client: aioredis.Redis, event_json_list: list):
    """
    Після успішної обробки події видаляємо її з processing queue.
    """
    async with client.pipeline() as pipe:
        for event_json in event_json_list:
            pipe.lrem(settings.REDIS_PROCESSING_KEY, 1, event_json)
        await pipe.execute()


async def recover_stack_events(client: aioredis.Redis):
    """
    Повертає всі події з processing queue назад у основну чергу.
    Використовується при старті воркера для відновлення незавершених подій.
    """
    source = settings.REDIS_PROCESSING_KEY
    dest = settings.REDIS_QUEUE_KEY

    count = 0
    while True:
        try:
            event = await client.lmove(source, dest)
            if event is None:
                break
            count += 1
        except RedisError as e:
            print(f"Redis error during recovery: {e}")

    if count > 0:
        print(f"Recovered {count} events from processing queue to main queue.")
