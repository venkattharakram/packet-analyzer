from scapy.all import sniff, rdpcap, get_if_list
import requests, time, os

# Mode & file inputs
MODE = os.getenv("MODE", "PCAP")        # MODE=LIVE or PCAP
PCAP_FILE = os.getenv("PCAP_FILE", "sample-pcaps/dns.cap")  # default file

# Parser service endpoint
# PARSER_URL = "http://parser-service:5001/parse"
PARSER_URL = "http://127.0.0.1:5001/parse"

def send_packet(pkt, source="LIVE"):
    """Send packet summary + raw hex + source to parser service"""
    data = {
        "raw": pkt.summary(),
        "hex": bytes(pkt).hex(),
        "source": source
    }
    try:
        requests.post(PARSER_URL, json=data)
    except Exception as e:
        print("Error sending to parser:", e)

def get_default_iface():
    """Auto-detect a usable network interface"""
    iface = os.getenv("IFACE")
    if iface:
        return iface
    for candidate in ["enp39s0", "ens5", "eth0", "wlan0"]:
        if candidate in get_if_list():
            return candidate
    raise RuntimeError("No suitable network interface found. Available: " + str(get_if_list()))

if __name__ == "__main__":
    time.sleep(5)  # wait for other services to start

    if MODE.upper() == "LIVE":
        iface = get_default_iface()
        print(f"🔴 Sniffing live packets on {iface}...")
        sniff(iface=iface, prn=lambda pkt: send_packet(pkt, "LIVE"))
    else:
        print(f"🔵 Reading from PCAP file: {PCAP_FILE}")
        try:
            packets = rdpcap(PCAP_FILE)
            print(f"✅ Loaded {len(packets)} packets from {PCAP_FILE}")
            for pkt in packets:
                send_packet(pkt, "PCAP")
            print("🎉 Finished sending all packets from PCAP.")
        except Exception as e:
            print(f"❌ Error reading {PCAP_FILE}: {e}")
