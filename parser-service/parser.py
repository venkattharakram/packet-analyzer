from flask import Flask, request, jsonify
import requests
from scapy.all import Ether, IP, IPv6, TCP, UDP, DNS, DNSQR, ICMP, ARP, DHCP, SNMP
import time

app = Flask(__name__)
PERSISTOR_URL = "http://persistor-service:5002/store"

def post_to_persistor(payload, retries=5, delay=2):
    for _ in range(retries):
        try:
            requests.post(PERSISTOR_URL, json=payload, timeout=5)
            return True
        except Exception as e:
            print("Persistor not ready, retrying...", e)
            time.sleep(delay)
    print("Failed to persist packet after retries")
    return False

@app.route("/parse", methods=["POST"])
def parse_packet():
    pkt_data = request.json
    structured = {
        "src_ip": None, "dst_ip": None,
        "src_port": None, "dst_port": None,
        "protocol": "Other", "dns_query": None,
        "summary": pkt_data["raw"]
    }

    try:
        scapy_pkt = Ether(bytes.fromhex(pkt_data["hex"]))

        # ARP
        if scapy_pkt.haslayer(ARP):
            structured["protocol"] = "ARP"
            structured["src_ip"] = scapy_pkt[ARP].psrc
            structured["dst_ip"] = scapy_pkt[ARP].pdst

        # IPv4
        elif scapy_pkt.haslayer(IP):
            structured["src_ip"] = scapy_pkt[IP].src
            structured["dst_ip"] = scapy_pkt[IP].dst

            if scapy_pkt.haslayer(TCP):
                structured["src_port"] = scapy_pkt[TCP].sport
                structured["dst_port"] = scapy_pkt[TCP].dport
                if 80 in [scapy_pkt[TCP].sport, scapy_pkt[TCP].dport]:
                    structured["protocol"] = "HTTP"
                elif 443 in [scapy_pkt[TCP].sport, scapy_pkt[TCP].dport]:
                    structured["protocol"] = "HTTPS"
                else:
                    structured["protocol"] = "TCP"

            elif scapy_pkt.haslayer(UDP):
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
                if 53 in [scapy_pkt[UDP].sport, scapy_pkt[UDP].dport]:
                    structured["protocol"] = "DNS"
                    if scapy_pkt.haslayer(DNSQR):
                        structured["dns_query"] = scapy_pkt[DNSQR].qname.decode()
                elif scapy_pkt[UDP].sport in [67, 68] or scapy_pkt[UDP].dport in [67, 68]:
                    structured["protocol"] = "DHCP"
                elif scapy_pkt[UDP].sport in [161, 162] or scapy_pkt[UDP].dport in [161, 162]:
                    structured["protocol"] = "SNMP"
                else:
                    structured["protocol"] = "UDP"

            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"

        # IPv6
        elif scapy_pkt.haslayer(IPv6):
            structured["src_ip"] = scapy_pkt[IPv6].src
            structured["dst_ip"] = scapy_pkt[IPv6].dst
            structured["protocol"] = "IPv6"

    except Exception as e:
        print("Parse error:", e)

    post_to_persistor(structured)
    return jsonify({"status": "parsed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
