from flask import Flask, request, jsonify
import requests
from scapy.all import Ether, IP, IPv6, TCP, UDP, DNS, DNSQR, ICMP, ARP
from datetime import datetime

app = Flask(__name__)

# Persistor endpoint
PERSISTOR_URL = "http://127.0.0.1:5002/store"

@app.route("/parse", methods=["POST"])
def parse_packet():
    pkt_data = request.json
    structured = {
        "src_ip": "-",
        "dst_ip": "-",
        "src_port": None,
        "dst_port": None,
        "protocol": "Others",
        "dns_query": None,
        "summary": pkt_data.get("raw", ""),
        "timestamp": datetime.utcnow().isoformat(),
        "source": pkt_data.get("source", "LIVE")   # capture.py sends this
    }

    try:
        scapy_pkt = Ether(bytes.fromhex(pkt_data["hex"]))

        # ARP
        if scapy_pkt.haslayer(ARP):
            structured["src_ip"] = scapy_pkt[ARP].psrc
            structured["dst_ip"] = scapy_pkt[ARP].pdst
            structured["protocol"] = "ARP"

        # IPv4
        elif scapy_pkt.haslayer(IP):
            structured["src_ip"] = scapy_pkt[IP].src
            structured["dst_ip"] = scapy_pkt[IP].dst
            if scapy_pkt.haslayer(TCP):
                structured["src_port"] = scapy_pkt[TCP].sport
                structured["dst_port"] = scapy_pkt[TCP].dport
                structured["protocol"] = "HTTP" if 80 in [structured["src_port"], structured["dst_port"]] else "TCP"
            elif scapy_pkt.haslayer(UDP):
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
                structured["protocol"] = "DNS" if 53 in [structured["src_port"], structured["dst_port"]] else "UDP"
                if scapy_pkt.haslayer(DNSQR):
                    structured["dns_query"] = scapy_pkt[DNSQR].qname.decode(errors="ignore")
            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"

        # IPv6
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
                structured["protocol"] = "DNS" if 53 in [structured["src_port"], structured["dst_port"]] else "UDP"
            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"
            else:
                structured["protocol"] = "IPv6"

    except Exception as e:
        print("Parse error:", e)

    try:
        requests.post(PERSISTOR_URL, json=structured)
    except Exception as e:
        print("Persistor not ready:", e)

    return jsonify({"status": "parsed"})
