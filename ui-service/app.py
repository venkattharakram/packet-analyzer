from flask import Flask, render_template, request
import requests

app = Flask(__name__)
ANALYZER_URL = "http://analyzer-service:5003"

@app.route("/")
def index():
    protocol = request.args.get("protocol")
    packets = []
    summary = {}
    try:
        summary = requests.get(f"{ANALYZER_URL}/summary").json()
        if protocol:
            packets = requests.get(f"{ANALYZER_URL}/filter?protocol={protocol}").json()
        else:
            packets = requests.get(f"{ANALYZER_URL}/packets").json()
    except:
        pass
    return render_template("index.html", packets=packets, summary=summary, selected=protocol)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
