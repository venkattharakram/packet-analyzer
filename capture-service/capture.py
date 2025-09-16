from scapy.all import sniff, rdpcap
import requests, time, os

MODE = os.getenv("MODE", "PCAP")  # MODE=LIVE or PCAP
PCAP_FILE = "/pcaps/dns.cap"
PARSER_URL = "http://parser-service:5001/parse"

def send_packet(pkt):
    data = {"raw": pkt.summary(), "hex": bytes(pkt).hex()}
    try:
        requests.post(PARSER_URL, json=data)
    except Exception as e:
        print("Error sending to parser:", e)

if __name__ == "__main__":
    time.sleep(5)
    if MODE.upper() == "LIVE":
        print("Sniffing live packets on eth0...")
        sniff(iface="eth0", prn=send_packet, count=50)
    else:
        print(f"Reading from PCAP file: {PCAP_FILE}")
        packets = rdpcap(PCAP_FILE)
        for pkt in packets[:50]:
            send_packet(pkt)
