from flask import Flask, request, jsonify
from scapy.all import sniff, rdpcap, get_if_list
from scapy.utils import PcapReader
import requests, time, os, threading, logging, netifaces

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Parser endpoint inside Docker network
#PARSER_URL = "http://parser-service:5001/parse"
PARSER_URL = "http://127.0.0.1:5001/parse"

sniff_thread = None
stop_flag = False


def send_packet(pkt, source="LIVE"):
    """Send packet data to parser service"""
    data = {
        "raw": pkt.summary(),
        "hex": bytes(pkt).hex(),
        "source": source
    }
    try:
        resp = requests.post(PARSER_URL, json=data, timeout=3)
        if resp.status_code == 200:
            logging.info(f"Sent packet → {source} {data.get('raw')[:50]}")
    except Exception as e:
        logging.error(f"Error sending to parser: {e}")


def get_default_iface():
    """Auto-detect the default host network interface"""
    # 1. Check env var (manual override)
    iface = os.getenv("IFACE")
    if iface and iface in get_if_list():
        logging.info(f"🌐 Using IFACE from env: {iface}")
        return iface

    # 2. Try to detect default gateway interface
    try:
        gws = netifaces.gateways()
        if 'default' in gws and netifaces.AF_INET in gws['default']:
            iface = gws['default'][netifaces.AF_INET][1]
            logging.info(f"🌐 Auto-detected default interface: {iface}")
            return iface
    except Exception as e:
        logging.warning(f"⚠️ Failed to detect interface via gateways: {e}")

    # 3. Fallback: check common names
    for candidate in ["ens5", "eth0", "enp39s0", "wlan0", "lo"]:
        if candidate in get_if_list():
            logging.info(f"🌐 Fallback interface detected: {candidate}")
            return candidate

    # 4. Last resort: pick first available
    available = get_if_list()
    if available:
        logging.info(f"🌐 Defaulting to first available interface: {available[0]}")
        return available[0]

    raise RuntimeError("❌ No suitable network interface found. Available: " + str(get_if_list()))


def run_sniffer(mode="LIVE", pcap_file=None):
    """Run live or PCAP sniffing"""
    global stop_flag
    stop_flag = False
    time.sleep(2)

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
        except Exception:
            try:
                with PcapReader(file_to_read) as pcap_reader:
                    packets = [pkt for pkt in pcap_reader]
            except Exception as e2:
                logging.error(f"❌ Could not read {file_to_read}: {e2}")
                packets = []

        logging.info(f"✅ Loaded {len(packets)} packets from {file_to_read}")
        for pkt in packets:
            if stop_flag:
                break
            send_packet(pkt, source="PCAP")
        logging.info("🎉 Finished sending all packets from PCAP.")


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
    MODE = os.getenv("MODE")
    PCAP_FILE = os.getenv("PCAP_FILE")

    if MODE:  # manual sniffing
        run_sniffer(MODE, PCAP_FILE)
    else:     # API mode
        app.run(host="0.0.0.0", port=5004)
