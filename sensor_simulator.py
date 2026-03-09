import requests
import random
import time

URL = "http://127.0.0.1:5000/sensor-data"

WORKERS = ["W001", "W002", "W003"]

while True:
    for w in WORKERS:

        data = {
            "worker_id": w,
            "temperature": round(random.uniform(35.0, 40.5), 1),
            "heartbeat": random.randint(60, 110),
            "mq7": random.randint(50, 400),
            "mq2": random.randint(50, 500),
            "fall": random.choice([True, False])
        }

        try:
            r = requests.post(URL, json=data)
            print(w, r.json())
        except Exception as e:
            print("Server error:", e)

    time.sleep(25)