import argparse
import os
import threading
import time
from flask import Flask, request, jsonify
from scapy.all import sniff, rdpcap, get_if_list
from scapy.utils import PcapReader
import requests

app = Flask(__name__)

# Parser service URL
PARSER_URL = os.getenv("PARSER_URL", "http://127.0.0.1:5001/parse")

sniff_thread = None
stop_flag = False


def send_packet(pkt, source="LIVE"):
    """Send packet to parser-service"""
    data = {
        "raw": pkt.summary(),
        "hex": bytes(pkt).hex(),
        "source": source,
    }
    try:
        print(f"📤 Preparing to send packet to parser ({source}): {pkt.summary()}", flush=True)
        res = requests.post(PARSER_URL, json=data, timeout=2)
        print(f"✅ Parser response {res.status_code}: {res.text[:100]}", flush=True)
    except Exception as e:
        print(f"❌ Error sending to parser: {e}", flush=True)


def get_default_iface():
    """Pick default interface (or from env IFACE)"""
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


def run_sniffer(mode="LIVE", pcap_file=None, num_pkts=0):
    """Run live sniffer or replay PCAP"""
    global stop_flag
    stop_flag = False
    time.sleep(1)

    print(f"🚀 run_sniffer invoked (mode={mode}, file={pcap_file}, num={num_pkts})", flush=True)

    if mode.upper() == "LIVE":
        try:
            iface = get_default_iface()
            print(f"🔴 About to sniff on iface={iface}, count={num_pkts or '∞'}", flush=True)
            sniff(
                iface=iface,
                prn=lambda pkt: not stop_flag and send_packet(pkt, source="LIVE"),
                store=False,
                count=num_pkts if num_pkts > 0 else 0,
            )
            print("🎉 Sniff loop exited normally", flush=True)
        except Exception as e:
            print(f"❌ Sniff failed on iface: {e}", flush=True)
        finally:
            print("⚠️ run_sniffer thread terminated", flush=True)

    else:
        file_to_read = pcap_file or "sample-pcaps/dns.cap"
        print(f"🔵 Reading from PCAP file: {file_to_read}", flush=True)

        packets = []
        try:
            packets = rdpcap(file_to_read)
            print(f"📦 rdpcap loaded {len(packets)} packets", flush=True)
        except Exception:
            try:
                with PcapReader(file_to_read) as pcap_reader:
                    packets = [pkt for pkt in pcap_reader]
                print(f"📦 PcapReader loaded {len(packets)} packets", flush=True)
            except Exception as e2:
                print(f"❌ Could not read {file_to_read}: {e2}", flush=True)
                return

        print(f"✅ Loaded {len(packets)} packets from {file_to_read}", flush=True)
        for idx, pkt in enumerate(packets[:num_pkts or len(packets)], start=1):
            if stop_flag:
                print("🛑 Stop flag set, breaking out of PCAP loop", flush=True)
                break
            print(f"➡️ Sending packet #{idx}/{len(packets)}", flush=True)
            send_packet(pkt, source="PCAP")
        print("🎉 Finished sending all packets from PCAP.", flush=True)


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
    print("🛑 Stop sniffing requested (flag set=True)", flush=True)
    return jsonify({"status": "sniffing_stopped"})


# 🔎 Debug endpoint: list available interfaces
@app.route("/interfaces", methods=["GET"])
def get_interfaces():
    try:
        ifaces = get_if_list()
        print(f"📡 Available interfaces: {ifaces}", flush=True)
        return jsonify({"interfaces": ifaces})
    except Exception as e:
        print(f"❌ Failed to get interfaces: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


# CLI entrypoint
def parse_args():
    parser = argparse.ArgumentParser(description="Packet Capture Service")
    subparsers = parser.add_subparsers(dest="mode")

    live_parser = subparsers.add_parser("live", help="Live packet capture")
    live_parser.add_argument("--iface", help="Interface name")
    live_parser.add_argument("--num-pkts", type=int, default=0, help="Number of packets (0=∞)")

    pcap_parser = subparsers.add_parser("pcap", help="PCAP file capture")
    pcap_parser.add_argument("--pcap-file", required=True, help="Path to PCAP file")
    pcap_parser.add_argument("--num-pkts", type=int, default=0, help="Number of packets (0=all)")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "live":
        if args.iface:
            os.environ["IFACE"] = args.iface
        run_sniffer("LIVE", num_pkts=args.num_pkts)
    elif args.mode == "pcap":
        run_sniffer("PCAP", pcap_file=args.pcap_file, num_pkts=args.num_pkts)
    else:
        # Default to API mode
        app.run(host="0.0.0.0", port=5004)

