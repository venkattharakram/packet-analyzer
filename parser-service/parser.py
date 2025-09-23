from flask import Flask, request, jsonify
import requests
from scapy.all import Ether, IP, IPv6, TCP, UDP, DNS, DNSQR, ICMP, ARP
from datetime import datetime
import logging
import time 

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Persistor endpoint
#PERSISTOR_URL = "http://127.0.0.1:5002/store"
PERSISTOR_URL = "http://persistor-service:5002/store"


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

# Optional retry delay for persistor
def send_to_persistor(data, retries=5, delay=2):
    for attempt in range(retries):
        try:
            resp = requests.post(PERSISTOR_URL, json=data, timeout=5)
            if resp.status_code == 200:
                logging.info(f"✅ Packet sent to persistor: {data.get('protocol')}")
                return True
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt+1}/{retries} failed: {e}")
        time.sleep(delay)
    logging.error(f"❌ Failed to send packet after {retries} attempts")
    return False

@app.route("/parse", methods=["POST"])
def parse_packet():
    pkt_data = request.json
    structured = {
        "src_ip": "-",
        "dst_ip": "-",
        "src_port": None,
        "dst_port": None,
        "protocol": "Others",   # default fallback
        "dns_query": None,
        "summary": pkt_data.get("raw", ""),  # ✅ summary restored
        "timestamp": datetime.utcnow().isoformat(),
        "source": pkt_data.get("source", "LIVE")  # ✅ LIVE or PCAP
    }

    try:
        scapy_pkt = Ether(bytes.fromhex(pkt_data["hex"]))

        # ---- ARP ----
        if scapy_pkt.haslayer(ARP):
            structured["src_ip"] = scapy_pkt[ARP].psrc
            structured["dst_ip"] = scapy_pkt[ARP].pdst
            structured["protocol"] = "ARP"

        # ---- IPv4 ----
        elif scapy_pkt.haslayer(IP):
            structured["src_ip"] = scapy_pkt[IP].src
            structured["dst_ip"] = scapy_pkt[IP].dst

            if scapy_pkt.haslayer(TCP):
                structured["src_port"] = scapy_pkt[TCP].sport
                structured["dst_port"] = scapy_pkt[TCP].dport
                structured["protocol"] = (
                    "HTTP" if 80 in [scapy_pkt[TCP].sport, scapy_pkt[TCP].dport] else "TCP"
                )

            elif scapy_pkt.haslayer(UDP):
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
                structured["protocol"] = (
                    "DNS" if 53 in [scapy_pkt[UDP].sport, scapy_pkt[UDP].dport] else "UDP"
                )
                if scapy_pkt.haslayer(DNSQR):
                    structured["dns_query"] = scapy_pkt[DNSQR].qname.decode(errors="ignore")

            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"

        # ---- IPv6 ----
        elif scapy_pkt.haslayer(IPv6):
            structured["src_ip"] = scapy_pkt[IPv6].src
            structured["dst_ip"] = scapy_pkt[IPv6].dst

            if scapy_pkt.haslayer(TCP):
                structured["src_port"] = scapy_pkt[TCP].sport
                structured["dst_port"] = scapy_pkt[TCP].dport
                structured["protocol"] = "TCP"

            elif scapy_pkt.haslayer(UDP):
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
                structured["protocol"] = (
                    "DNS" if 53 in [scapy_pkt[UDP].sport, scapy_pkt[UDP].dport] else "UDP"
                )

            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"

            else:
                structured["protocol"] = "IPv6"

    except Exception as e:
        print("Parse error:", e)

    # ---- Send structured packet to persistor ----
    try:
        requests.post(PERSISTOR_URL, json=structured)
    except Exception as e:
        print("Persistor not ready:", e)

    return jsonify({"status": "parsed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)