import random
import time

import requests

API_URL = "http://localhost:8000/ingest/track"

# Імітуємо різні ендпоінти та затримки
PATHS = ["/api/users", "/api/orders", "/api/auth", "/home", "/contact"]
METHODS = ["GET", "POST", "PUT"]


def generate_http_log():
    method = random.choice(METHODS)
    path = random.choice(PATHS)
    status = random.choice([200, 201, 400, 500])
    duration = random.randint(10, 500)

    log_string = f"{method} {path} {status} {duration}ms"

    return {
        "event": "page_view",
        "type": "http",
        "service": "backend-core",
        "source": "load-test-script",
        "user_id": str(random.randint(1, 1000)),
        "payload": {
            "raw_log": log_string,
            "extra": "load_test_data",
        },
    }


print("🚀 Starting Load Test... Press Ctrl+C to stop.")

try:
    while True:
        data = generate_http_log()
        try:
            requests.post(API_URL, json=data)
            # print(f"Sent: {data['payload']['raw_log']}")
        except Exception as e:
            print(f"Error: {e}")

        # Випадкова затримка, щоб графік був "живим" (від 0.01 до 0.1 сек)
        time.sleep(random.uniform(0.01, 0.1))
except KeyboardInterrupt:
    print("\n🛑 Stopped.")
