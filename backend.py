from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import os
import google.generativeai as genai

# ---------- GEMINI API ----------
genai.configure(api_key=os.getenv("AIzaSyCIcOYsKmjeAOZGM407UIJLAxysxSIDGl0"))
model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)
CORS(app)

workers = {}

# ---------- HOME PAGE ----------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------- AI ANALYSIS ----------
def analyze_condition(temp, heartbeat, mq7, mq2, fall):

    prompt = f"""
    A worker is wearing a smart safety helmet.

    Body Temperature: {temp} °C
    Heartbeat: {heartbeat} BPM
    MQ7 Gas Level: {mq7}
    MQ2 Gas Level: {mq2}
    Fall Detected: {fall}

    Decide if the worker is SAFE or in DANGEROUS condition.
    Reply with only ONE word:
    SAFE or DANGEROUS
    """

    try:
        response = model.generate_content(prompt)
        decision = response.text.strip().upper()

        if decision == "DANGEROUS":
            return "BAD"
        else:
            return "GOOD"

    except Exception as e:
        print("Gemini error, using fallback:", e)

        # ---------- RULE BASED SAFETY ----------
        if temp > 39:
            return "BAD"

        if heartbeat < 50 or heartbeat > 120:
            return "BAD"

        if mq7 > 300 or mq2 > 400:
            return "BAD"

        if fall:
            return "BAD"

        return "GOOD"


# ---------- SENSOR DATA ----------
@app.route("/sensor-data", methods=["POST"])
def receive_data():

    data = request.json

    worker_id = data.get("worker_id")

    temp = data.get("temperature")
    heartbeat = data.get("heartbeat")
    mq7 = data.get("mq7")
    mq2 = data.get("mq2")
    fall = data.get("fall")

    status = analyze_condition(temp, heartbeat, mq7, mq2, fall)

    workers[worker_id] = {
        "temperature": temp,
        "heartbeat": heartbeat,
        "mq7": mq7,
        "mq2": mq2,
        "fall": fall,
        "status": status,
        "last_seen": time.time()
    }

    alert = status == "BAD"

    if alert:
        print(f"🚨 ALERT! Worker {worker_id} in danger!")

    return jsonify({
        "status": status,
        "alert": alert
    })


# ---------- DASHBOARD DATA ----------
@app.route("/dashboard", methods=["GET"])
def dashboard():

    active = {}

    for k, v in workers.items():
        if time.time() - v["last_seen"] < 20:
            active[k] = v

    return jsonify({
        "worker_count": len(active),
        "workers": active
    })


# ---------- SERVER START ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)