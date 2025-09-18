from flask import Flask, jsonify
import threading
from scapy.all import sniff

app = Flask(__name__)

sniffer_thread = None
stop_sniffer = threading.Event()

def sniff_packets():
    sniff(prn=lambda pkt: print(pkt.summary()), stop_filter=lambda x: stop_sniffer.is_set())

@app.route("/start_sniffing", methods=["POST"])
def start_sniffing():
    global sniffer_thread, stop_sniffer
    if sniffer_thread and sniffer_thread.is_alive():
        return jsonify({"status": "already running"})
    stop_sniffer.clear()
    sniffer_thread = threading.Thread(target=sniff_packets, daemon=True)
    sniffer_thread.start()
    return jsonify({"status": "sniffing started"})

@app.route("/stop_sniffing", methods=["POST"])
def stop_sniffing():
    global stop_sniffer
    stop_sniffer.set()
    return jsonify({"status": "sniffing stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
