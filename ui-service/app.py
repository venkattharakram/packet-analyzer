from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ANALYZER_URL = "http://127.0.0.1:5003"

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

@app.route("/")
def index():
    protocol = request.args.get("protocol")
    source = request.args.get("source")
    packets, summary = [], {}

    try:
        summary = requests.get(f"{ANALYZER_URL}/protocol_summary").json()
        if source:
            packets = requests.get(f"{ANALYZER_URL}/filter_by_source?source={source}").json()
        elif protocol and protocol != "ALL":
            packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}").json()
        else:
            packets = requests.get(f"{ANALYZER_URL}/packets").json()
    except Exception as e:
        print("UI Error:", e)

    return render_template("index.html", packets=packets, summary=summary, selected=protocol, source=source)

@app.route("/api/filter_by_source", methods=["GET"])
def api_filter_by_source():
    source = request.args.get("source")
    try:
        return jsonify(requests.get(f"{ANALYZER_URL}/filter_by_source?source={source}").json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
