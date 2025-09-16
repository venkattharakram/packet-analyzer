from flask import Flask, request, jsonify
import requests
from scapy.all import Ether, IP, TCP, UDP, DNS, DNSQR, ICMP

app = Flask(__name__)
PERSISTOR_URL = "http://persistor-service:5002/store"

@app.route("/parse", methods=["POST"])
def parse_packet():
    pkt_data = request.json
    structured = {
        "src_ip": None, "dst_ip": None,
        "src_port": None, "dst_port": None,
        "protocol": "Unknown", "dns_query": None,
        "summary": pkt_data["raw"]
    }
    try:
        scapy_pkt = Ether(bytes.fromhex(pkt_data["hex"]))
        if scapy_pkt.haslayer(IP):
            structured["src_ip"] = scapy_pkt[IP].src
            structured["dst_ip"] = scapy_pkt[IP].dst
            if scapy_pkt.haslayer(TCP):
                structured["src_port"] = scapy_pkt[TCP].sport
                structured["dst_port"] = scapy_pkt[TCP].dport
                structured["protocol"] = "HTTP" if 80 in [scapy_pkt[TCP].sport, scapy_pkt[TCP].dport] else "TCP"
            elif scapy_pkt.haslayer(UDP):
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
                structured["protocol"] = "DNS" if 53 in [scapy_pkt[UDP].sport, scapy_pkt[UDP].dport] else "UDP"
                if scapy_pkt.haslayer(DNSQR):
                    structured["dns_query"] = scapy_pkt[DNSQR].qname.decode()
            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"
    except Exception as e:
        print("Parse error:", e)

    try:
        requests.post(PERSISTOR_URL, json=structured)
    except Exception as e:
        print("Persistor not ready:", e)

    return jsonify({"status": "parsed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
