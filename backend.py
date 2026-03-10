from flask import Flask, request, jsonify
import os
import time

app = Flask(__name__)

workers = {}

@app.route("/")
def home():
    return "Smart Helmet Server Running"

@app.route("/sensor", methods=["POST"])
def receive_sensor():

    data = request.json

    worker_id = data.get("worker_id","W001")

    workers[worker_id] = {
        "pulse": data.get("pulse",0),
        "temperature": data.get("temperature",0),
        "mq2": data.get("mq2",0),
        "mq7": data.get("mq7",0),
        "motion": data.get("motion","normal"),
        "last_seen": time.time()
    }

    print("Update:",workers[worker_id])

    return jsonify({"status":"ok"})


@app.route("/dashboard")
def dashboard():

    active = {}

    for k,v in workers.items():

        if time.time() - v["last_seen"] < 30:
            active[k] = v

    return jsonify({
        "workers":active,
        "count":len(active)
    })


if __name__ == "__main__":

    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)