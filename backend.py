from flask import Flask, request, jsonify, render_template
import os
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

workers = {}


# -------------------------
# SAFETY CHECK
# -------------------------
def check_worker_status(heartbeat, temperature, mq7, mq2, fall):

    if temperature > 39:
        return "BAD"

    if heartbeat < 50 or heartbeat > 120:
        return "BAD"

    if mq7 > 300 or mq2 > 400:
        return "BAD"

    if fall == True:
        return "BAD"

    return "GOOD"


# -------------------------
# WEBSITE
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# SENSOR DATA FROM HELMET
# -------------------------
@app.route("/sensor-data", methods=["POST"])
def receive_sensor():

    data = request.json
    worker_id = data.get("worker_id", "W001")

    temperature = data.get("temperature", 0)
    heartbeat = data.get("heartbeat", 0)
    mq7 = data.get("mq7", 0)
    mq2 = data.get("mq2", 0)
    fall = data.get("fall", False)

    status = check_worker_status(heartbeat, temperature, mq7, mq2, fall)

    workers[worker_id] = {
        "temperature": temperature,
        "heartbeat": heartbeat,
        "mq7": mq7,
        "mq2": mq2,
        "fall": fall,
        "status": status,
        "last_seen": time.time()
    }

    print("Worker Update:", workers[worker_id])

    return jsonify({
        "status": status,
        "alert": status == "BAD"
    })


# -------------------------
# DASHBOARD DATA
# -------------------------
@app.route("/dashboard")
def dashboard():

    active_workers = {}

    for worker_id, data in workers.items():
        if time.time() - data["last_seen"] < 30:
            active_workers[worker_id] = data

    return jsonify({
        "worker_count": len(active_workers),
        "workers": active_workers
    })


# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)