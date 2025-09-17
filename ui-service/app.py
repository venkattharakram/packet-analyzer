from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz

app = Flask(__name__)
# ANALYZER_URL = "http://analyzer-service:5003"
ANALYZER_URL = "http://127.0.0.1:5003"

# --- Custom Jinja filters for datetime handling ---
@app.template_filter('to_datetime')
def to_datetime(value):
    """Convert ISO string to datetime object"""
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

@app.template_filter('to_ist')
def to_ist(value):
    """Convert datetime object (UTC) to IST string"""
    try:
        tz = pytz.timezone('Asia/Kolkata')
        return value.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return value

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
