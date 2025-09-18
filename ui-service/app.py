from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Point to analyzer
ANALYZER_URL = "http://127.0.0.1:5003"

# --- Custom Jinja filters ---
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

# --- UI route ---
@app.route("/")
def index():
    protocol = request.args.get("protocol")
    packets, summary, mode = [], {}, "Unknown"

    try:
        summary = requests.get(f"{ANALYZER_URL}/protocol_summary").json()
        mode = requests.get(f"{ANALYZER_URL}/mode").json().get("mode", "Unknown")

        if protocol and protocol != "ALL":
            packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}").json()
        elif protocol == "ALL":
            packets = requests.get(f"{ANALYZER_URL}/all_packets").json()
        else:
            packets = requests.get(f"{ANALYZER_URL}/packets").json()
    except Exception as e:
        print("UI Error:", e)

    return render_template("index.html", 
                           packets=packets, 
                           summary=summary, 
                           selected=protocol, 
                           mode=mode)

# --- APIs ---
@app.route("/api/packets", methods=["GET"])
def api_packets():
    try:
        packets = requests.get(f"{ANALYZER_URL}/packets").json()
        return jsonify(packets)
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
    if not protocol:
        return jsonify({"error": "Missing 'protocol' parameter"}), 400

    try:
        packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}").json()
        return jsonify(packets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
