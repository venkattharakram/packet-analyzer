from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz
from flask_cors import CORS   # ✅ added this

app = Flask(__name__)
CORS(app)   # ✅ enable CORS

# ANALYZER_URL = "http://analyzer-service:5003"
ANALYZER_URL = "http://127.0.0.1:5003"

# --- Custom Jinja filters for datetime handling ---
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

# --- HTML Dashboard ---
@app.route("/")
def index():
    protocol = request.args.get("protocol")
    packets = []
    summary = {}
    try:
        summary = requests.get(f"{ANALYZER_URL}/protocol_summary").json()
        if protocol:
            packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}").json()
        else:
            packets = requests.get(f"{ANALYZER_URL}/packets").json()
    except Exception as e:
        print("UI Error:", e)
    return render_template("index.html", packets=packets, summary=summary, selected=protocol)

# --- JSON APIs ---
@app.route("/api/packets", methods=["GET"])
def api_packets():
    """Return packets with pagination"""
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    offset = (page - 1) * limit

    try:
        packets = requests.get(f"{ANALYZER_URL}/packets").json()
        paginated = packets[offset:offset + limit]
        return jsonify({
            "page": page,
            "limit": limit,
            "total": len(packets),
            "packets": paginated
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/summary", methods=["GET"])
def api_summary():
    """Return protocol summary as JSON"""
    try:
        summary = requests.get(f"{ANALYZER_URL}/protocol_summary").json()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/filter", methods=["GET"])
def api_filter():
    """Return packets filtered by protocol with pagination"""
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify({"error": "Missing 'protocol' parameter"}), 400

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    offset = (page - 1) * limit

    try:
        packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}").json()
        paginated = packets[offset:offset + limit]
        return jsonify({
            "protocol": protocol,
            "page": page,
            "limit": limit,
            "total": len(packets),
            "packets": paginated
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ NEW ENDPOINT: all protocols grouped
@app.route("/api/all_protocols", methods=["GET"])
def api_all_protocols():
    """Return all packets grouped by protocol"""
    try:
        grouped = requests.get(f"{ANALYZER_URL}/all_protocols").json()
        return jsonify(grouped)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
