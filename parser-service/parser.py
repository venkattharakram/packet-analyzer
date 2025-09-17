from scapy.all import Ether, IP, IPv6, TCP, UDP, DNS, DNSQR, ICMP, ARP, ICMPv6EchoRequest, ICMPv6EchoReply

@app.route("/parse", methods=["POST"])
def parse_packet():
    pkt_data = request.json
    structured = {
        "src_ip": None, "dst_ip": None,
        "src_port": None, "dst_port": None,
        "protocol": "Others", "dns_query": None,
        "summary": pkt_data["raw"]
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
                structured["protocol"] = "HTTP" if 80 in [scapy_pkt[TCP].sport, scapy_pkt[TCP].dport] else "TCP"
            elif scapy_pkt.haslayer(UDP):
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
                structured["protocol"] = "DNS" if 53 in [scapy_pkt[UDP].sport, scapy_pkt[UDP].dport] else "UDP"
                if scapy_pkt.haslayer(DNSQR):
                    structured["dns_query"] = scapy_pkt[DNSQR].qname.decode()
            elif scapy_pkt.haslayer(ICMP):
                structured["protocol"] = "ICMP"

        # ---- IPv6 ----
        elif scapy_pkt.haslayer(IPv6):
            structured["src_ip"] = scapy_pkt[IPv6].src
            structured["dst_ip"] = scapy_pkt[IPv6].dst
            if scapy_pkt.haslayer(TCP):
                structured["protocol"] = "TCP"
                structured["src_port"] = scapy_pkt[TCP].sport
                structured["dst_port"] = scapy_pkt[TCP].dport
            elif scapy_pkt.haslayer(UDP):
                structured["protocol"] = "DNS" if 53 in [scapy_pkt[UDP].sport, scapy_pkt[UDP].dport] else "UDP"
                structured["src_port"] = scapy_pkt[UDP].sport
                structured["dst_port"] = scapy_pkt[UDP].dport
            elif scapy_pkt.haslayer(ICMPv6EchoRequest) or scapy_pkt.haslayer(ICMPv6EchoReply):
                structured["protocol"] = "ICMP"
            else:
                structured["protocol"] = "IPv6"

        # ---- Default fallback ----
        if structured["protocol"] == "Unknown":
            structured["protocol"] = "Others"

    except Exception as e:
        print("Parse error:", e)

    try:
        requests.post(PERSISTOR_URL, json=structured)
    except Exception as e:
        print("Persistor not ready:", e)

    return jsonify({"status": "parsed"})
