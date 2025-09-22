from flask import Flask, request, jsonify
from scapy.all import sniff, rdpcap, get_if_list
from scapy.utils import PcapReader
import requests, time, os, threading

app = Flask(__name__)

 #PARSER_URL = "http://127.0.0.1:5001/parse"
PARSER_URL = "http://parser-service:5001/parse"

sniff_thread = None
stop_flag = False

def send_packet(pkt, source="LIVE"):
    data = {
        "raw": pkt.summary(),
        "hex": bytes(pkt).hex(),
        "source": source
    }
    try:
        resp = requests.post(PARSER_URL, json=data, timeout=5)
        print(f"Sent to parser → status {resp.status_code}")
    except Exception as e:
        print("Error sending to parser:", e)

def get_default_iface():
    iface = os.getenv("IFACE")
    if iface:
        return iface
    for candidate in ["enp39s0", "ens5", "eth0", "wlan0"]:
        if candidate in get_if_list():
            return candidate
    raise RuntimeError("No suitable network interface found. Available: " + str(get_if_list()))

def run_sniffer(mode="LIVE", pcap_file=None):
    global stop_flag
    stop_flag = False
    time.sleep(2)

    if mode.upper() == "LIVE":
        iface = get_default_iface()
        print(f"🔴 Sniffing live packets on {iface}...")
        sniff(iface=iface, prn=lambda pkt: not stop_flag and send_packet(pkt, source="LIVE"), store=False)
    else:
        file_to_read = pcap_file or "sample-pcaps/dns.cap"
        print(f"🔵 Reading from PCAP file: {file_to_read}")
        packets = []
        try:
            packets = rdpcap(file_to_read)
        except Exception:
            try:
                with PcapReader(file_to_read) as pcap_reader:
                    packets = [pkt for pkt in pcap_reader]
            except Exception as e2:
                print(f"❌ Could not read {file_to_read}: {e2}")
                packets = []

        print(f"✅ Loaded {len(packets)} packets from {file_to_read}")
        for pkt in packets:
            if stop_flag:
                break
            send_packet(pkt, source="PCAP")
        print("🎉 Finished sending all packets from PCAP.")

@app.route("/start_sniffing", methods=["POST"])
def start_sniffing():
    global sniff_thread, stop_flag
    if sniff_thread and sniff_thread.is_alive():
        return jsonify({"status": "already_running"}), 400

    mode = request.args.get("mode", "LIVE")
    pcap_file = request.args.get("file")

    sniff_thread = threading.Thread(target=run_sniffer, args=(mode, pcap_file))
    sniff_thread.start()
    return jsonify({"status": f"sniffing_started_{mode}", "pcap": pcap_file})

@app.route("/stop_sniffing", methods=["POST"])
def stop_sniffing():
    global stop_flag
    stop_flag = True
    return jsonify({"status": "sniffing_stopped"})

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "capture-service running",
        "available_endpoints": [
            "/health",
            "/start_sniffing",
            "/stop_sniffing"
        ]
    })


if __name__ == "__main__":
    # If run directly, still support manual env-based mode (backward compatible)
    MODE = os.getenv("MODE")
    PCAP_FILE = os.getenv("PCAP_FILE")

    if MODE:  # manual sniffing
        run_sniffer(MODE, PCAP_FILE)
    else:     # API mode
        app.run(host="0.0.0.0", port=5004)
