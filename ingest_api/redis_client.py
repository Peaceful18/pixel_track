import redis

from app_config.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    socket_timeout=5,
    decode_responses=True,
)


def push_event(event_json: str) -> None:
    """
    Проста операція O(1) для вставки в кінець списку (LPUSH/RPUSH).
    Використовуємо LPUSH (Left Push), тоді воркер робитиме RPOP.
    """
    try:
        redis_client.lpush(settings.REDIS_QUEUE_KEY, event_json)
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        raise e


def push_event_batch(events_json: list[str]) -> None:
    """
    Використовує pipeline для масової вставки[cite: 501].
    Зменшує кількість RTT (Round Trip Time).
    """
    try:
        pipe = redis_client.pipeline()
        for event in events_json:
            pipe.lpush(settings.REDIS_QUEUE_KEY, event)
        pipe.execute()
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        raise e


def check_health() -> bool:
    """
    Перевірка з'єднання [cite: 509]
    """
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False
