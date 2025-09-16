from scapy.all import sniff, rdpcap, get_if_list
import requests, time, os

MODE = os.getenv("MODE", "PCAP")   # MODE=LIVE or PCAP
PCAP_FILE = "sample-pcaps/dns.cap"
PARSER_URL = "http://parser-service:5001/parse"

def send_packet(pkt):
    data = {"raw": pkt.summary(), "hex": bytes(pkt).hex()}
    try:
        requests.post(PARSER_URL, json=data)
    except Exception as e:
        print("Error sending to parser:", e)

def get_default_iface():
    # Prefer environment variable if set
    iface = os.getenv("IFACE")
    if iface:
        return iface
    # Otherwise try common names
    for candidate in ["ens5", "eth0", "wlan0"]:
        if candidate in get_if_list():
            return candidate
    raise RuntimeError("No suitable network interface found. Available: " + str(get_if_list()))

if __name__ == "__main__":
    time.sleep(5)

    if MODE.upper() == "LIVE":
        iface = get_default_iface()
        print(f"🔴 Sniffing live packets on {iface}...")
        sniff(iface=iface, prn=send_packet, count=50)
    else:
        print(f"🔵 Reading from PCAP file: {PCAP_FILE}")
        packets = rdpcap(PCAP_FILE)
        for pkt in packets[:50]:
            send_packet(pkt)
