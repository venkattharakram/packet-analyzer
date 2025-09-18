from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ANALYZER_URL = "http://127.0.0.1:5003"
CAPTURE_URL = "http://127.0.0.1:5004"   # 👈 capture service endpoint

@app.template_filter('to_datetime')
def to_datetime(value):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

@app.template_filter('to_ist')
def to_ist(value):
    try:
        tz = pytz.timezone('Asia/Kolkata')
        return value.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return value

# --- NEW: Start Sniffing ---
@app.route("/api/start_sniffing", methods=["POST"])
def start_sniffing():
    try:
        res = requests.post(f"{CAPTURE_URL}/start_sniffing")
        return jsonify({"status": "started", "response": res.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- NEW: Stop Sniffing ---
@app.route("/api/stop_sniffing", methods=["POST"])
def stop_sniffing():
    try:
        res = requests.post(f"{CAPTURE_URL}/stop_sniffing")
        return jsonify({"status": "stopped", "response": res.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    # existing index logic here
    ...
