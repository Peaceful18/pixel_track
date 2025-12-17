import json
import time

from parsers import parse_log
from redis_client import brpop_event
from sqlalchemy.exc import SQLAlchemyError

from database.database import SessionLocal
from database.models import RawEvent

BATCH_SIZE = 100
FLUSH_INTERVAL = 5
KEY_RAW_LOG = "raw_log"


def log_listener():
    buffer = []
    last_flus_time = time.monotonic()
    while True:
        data = brpop_event()
        if data:
            queue_name, payload_json = data
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
                    timestamp=event_data["timestamp"],
                )
                buffer.append(new_event)
            except json.JSONDecodeError:
                print(f"❌ Помилка: прийшов не JSON -> {payload_json}")
            except Exception as e:
                print(f"❌ Невідома помилка: {e}. Дані: {payload_json}")

        current_time = time.monotonic()
        is_batch_full = len(buffer) >= BATCH_SIZE
        is_interval_passed = current_time - last_flus_time >= FLUSH_INTERVAL
        if buffer and (is_batch_full or is_interval_passed):
            try:
                with SessionLocal() as db:
                    db.add_all(buffer)
                    db.commit()

                print(f"🚀 Flushed {len(buffer)} events to DB")

                buffer = []
                last_flus_time = time.monotonic()

            except SQLAlchemyError as e:
                print(f"❌ Помилка вставки в DB: {e}.")
                buffer = []
            except Exception as e:
                print(f"❌ Невідома помилка: {e}.")
                buffer = []


if __name__ == "__main__":
    print("Worker started...")
    log_listener()
