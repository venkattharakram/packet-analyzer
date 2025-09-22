import argparse
import os
import threading
import time
from flask import Flask, request, jsonify
from scapy.all import sniff, rdpcap, get_if_list
from scapy.utils import PcapReader
import requests, time, os, threading, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Parser service URL
PARSER_URL = os.getenv("PARSER_URL", "http://127.0.0.1:5001/parse")
# Parser endpoint inside Docker network
#PARSER_URL = "http://parser-service:5001/parse"
PARSER_URL = "http://127.0.0.1:5001/parse"

sniff_thread = None
stop_flag = False



def send_packet(pkt, source="LIVE"):
    """Send packet to parser-service"""
    """Send packet data to parser service"""
    data = {
        "raw": pkt.summary(),
        "hex": bytes(pkt).hex(),
        "source": source,
    }
    try:
        resp = requests.post(PARSER_URL, json=data, timeout=3)
        if resp.status_code == 200:
            logging.info(f"Sent packet → {source} {data.get('raw')[:50]}")
    except Exception as e:
        logging.error(f"Error sending to parser: {e}")


def get_default_iface():
    """Auto-detect interface"""
    iface = os.getenv("IFACE")
    if iface:
        print(f"⚙️ Using IFACE from env: {iface}", flush=True)
        return iface

    candidates = ["ens5", "eth0", "enp39s0", "wlan0"]
    available = get_if_list()
    print(f"🔎 Available interfaces: {available}", flush=True)

    for candidate in candidates:
        if candidate in available:
            print(f"✅ Selected default iface: {candidate}", flush=True)
            return candidate
    raise RuntimeError("No suitable network interface found. Available: " + str(available))



def run_sniffer(mode="LIVE", pcap_file=None):
    """Run live or PCAP sniffing"""
    global stop_flag
    stop_flag = False
    time.sleep(1)

    print(f"🚀 run_sniffer invoked (mode={mode}, file={pcap_file}, num={num_pkts})", flush=True)

    if mode.upper() == "LIVE":
        iface = get_default_iface()
        logging.info(f"🔴 Started sniffing on {iface}...")
        sniff(
            iface=iface,
            prn=lambda pkt: send_packet(pkt, source="LIVE"),
            store=False,
            stop_filter=lambda pkt: stop_flag   # ✅ stop sniffing gracefully
        )
        logging.info("🛑 Sniffing stopped (LIVE mode).")

    else:
        file_to_read = pcap_file or "sample-pcaps/dns.cap"
        logging.info(f"🔵 Reading from PCAP file: {file_to_read}")
        try:
            packets = rdpcap(file_to_read)
            print(f"📦 rdpcap loaded {len(packets)} packets", flush=True)
        except Exception:
            try:
                with PcapReader(file_to_read) as pcap_reader:
                    packets = [pkt for pkt in pcap_reader]
                print(f"📦 PcapReader loaded {len(packets)} packets", flush=True)
            except Exception as e2:
                logging.error(f"❌ Could not read {file_to_read}: {e2}")
                packets = []

        logging.info(f"✅ Loaded {len(packets)} packets from {file_to_read}")
        for pkt in packets:
            if stop_flag:
                print("🛑 Stop flag set, breaking out of PCAP loop", flush=True)
                break
            print(f"➡️ Sending packet #{idx}/{len(packets)}", flush=True)
            send_packet(pkt, source="PCAP")
        logging.info("🎉 Finished sending all packets from PCAP.")


@app.route("/start_sniffing", methods=["POST"])
def start_sniffing():
    global sniff_thread, stop_flag
    if sniff_thread and sniff_thread.is_alive():
        return jsonify({"status": "already_running"}), 400

    mode = request.args.get("mode", "LIVE")
    pcap_file = request.args.get("file")
    num_pkts = request.args.get("num", type=int, default=0)

    print(f"➡️ API called: start_sniffing(mode={mode}, file={pcap_file}, num={num_pkts})", flush=True)

    sniff_thread = threading.Thread(target=run_sniffer, args=(mode, pcap_file, num_pkts))
    sniff_thread.daemon = True
    sniff_thread.start()

    print("✅ Sniff thread started", flush=True)
    return jsonify({"status": f"sniffing_started_{mode}", "pcap": pcap_file, "limit": num_pkts})




@app.route("/stop_sniffing", methods=["POST"])
def stop_sniffing():
    global stop_flag
    stop_flag = True
    logging.info("🛑 Stop request received — stopping sniffer...")
    return jsonify({"status": "sniffing_stopped"})


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status": "capture-service running",
        "available_endpoints": ["/health", "/start_sniffing", "/stop_sniffing"]
    })


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


if __name__ == "__main__":
    # If run directly, still support manual env-based mode (backward compatible)
    MODE = os.getenv("MODE")
    PCAP_FILE = os.getenv("PCAP_FILE")

    if MODE:  # manual sniffing
        run_sniffer(MODE, PCAP_FILE)
    else:     # API mode
        app.run(host="0.0.0.0", port=5004)

