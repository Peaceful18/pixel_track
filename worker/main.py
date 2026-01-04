import asyncio
import json
import time
from datetime import datetime

from parsers import parse_log
from redis_client import ack_event_processed, get_event_reliable, recover_stack_events
from sqlalchemy.exc import SQLAlchemyError

from database.database import AsyncSessionLocal
from database.models import RawEvent
from infra.redis_provider import redis_provider

BATCH_SIZE = 100
FLUSH_INTERVAL = 5
KEY_RAW_LOG = "raw_log"


async def log_listener():
    buffer = []
    raw_payload_to_clean = []
    last_flush_time = time.monotonic()
    redis_provider.init_pool()
    async with redis_provider.get_client() as redis:
        await recover_stack_events(redis)
        while True:
            data = await get_event_reliable(redis)
            if data:
                payload_json = data
                try:
                    event_data = json.loads(payload_json)
                    event_type = event_data["type"]
                    payload = event_data.get("payload", {}) or {}
                    raw_message = payload.get(KEY_RAW_LOG)
                    if raw_message:
                        parsed_info = parse_log(raw_message, event_type)
                        if parsed_info:
                            payload.update(parsed_info)
                    new_event = RawEvent(
                        raw_event_name=event_data["event"],
                        raw_event_type=event_data["type"],
                        service=event_data["service"],
                        source=event_data["source"],
                        user_id=event_data["user_id"],
                        payload=event_data["payload"],
                        timestamp=datetime.fromisoformat(event_data["timestamp"]),
                    )
                    buffer.append(new_event)
                    raw_payload_to_clean.append(payload_json)
                except json.JSONDecodeError:
                    print(f"❌ Помилка: прийшов не JSON -> {payload_json}")
                    raw_payload_to_clean.append(payload_json)
                except Exception as e:
                    print(f"❌ Невідома помилка: {e}. Дані: {payload_json}")
                    raw_payload_to_clean.append(payload_json)

            current_time = time.monotonic()
            is_batch_full = len(buffer) >= BATCH_SIZE
            is_interval_passed = current_time - last_flush_time >= FLUSH_INTERVAL
            if buffer and (is_batch_full or is_interval_passed):
                try:
                    await flush_to_db(buffer)
                    await ack_event_processed(redis, raw_payload_to_clean)
                    buffer.clear()
                    raw_payload_to_clean.clear()
                    last_flush_time = time.monotonic()

                except SQLAlchemyError as e:
                    print(f"❌ Помилка вставки в DB: {e}.")
                except Exception as e:
                    print(f"❌ Невідома помилка: {e}.")
            if not data:
                await asyncio.sleep(0.1)


async def flush_to_db(events: list):
    if not events:
        return

    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                session.add_all(events)
            print(f"🚀 Flushed {len(events)} events to DB")
        except SQLAlchemyError as e:
            print(f"❌ Помилка вставки в DB: {e}.")
            raise


if __name__ == "__main__":
    print("Worker started...")
    try:
        asyncio.run(log_listener())
    except KeyboardInterrupt:
        print("Worker stopped manually.")
