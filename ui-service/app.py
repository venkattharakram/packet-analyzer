from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
ANALYZER_URL = "http://analyzer-service:5003"
CORS(app)

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
    protocol = request.args.get("protocol")
    source = request.args.get("source")
    packets, summary = [], {}
    try:
        summary = requests.get(f"{ANALYZER_URL}/protocol_summary").json()
        params = {}
        if source:
            params["source"] = source
        if protocol:
            packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}", params=params).json()
        else:
            packets = requests.get(f"{ANALYZER_URL}/packets", params=params).json()
    except Exception as e:
        print("UI Error:", e)
    return render_template("index.html", packets=packets, summary=summary, selected=protocol, selected_source=source)

# --- JSON APIs ---
@app.route("/api/packets", methods=["GET"])
def api_packets():
    try:
        packets = requests.get(f"{ANALYZER_URL}/packets").json()
        return jsonify({"limit": 50, "packets": packets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/summary", methods=["GET"])
def api_summary():
    try:
        summary = requests.get(f"{ANALYZER_URL}/protocol_summary").json()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/filter", methods=["GET"])
def api_filter():
    protocol = request.args.get("protocol")
    source = request.args.get("source")
    if not protocol:
        return jsonify({"error": "Missing 'protocol' parameter"}), 400
    try:
        params = {}
        if source:
            params["source"] = source
        packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}", params=params).json()
        return jsonify(packets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/all_protocols", methods=["GET"])
def api_all_protocols():
    try:
        packets = requests.get(f"{ANALYZER_URL}/all_protocols").json()
        return jsonify(packets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route("/health")
def health():
    return "OK", 200
