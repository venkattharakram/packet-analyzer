from scapy.all import sniff, rdpcap, get_if_list
from scapy.utils import PcapReader
import requests, time, os

# Mode & file inputs
MODE = os.getenv("MODE", "PCAP")        # MODE=LIVE or PCAP
PCAP_FILE = os.getenv("PCAP_FILE", "sample-pcaps/dns.cap")  # default
PARSER_URL = "http://127.0.0.1:5001/parse"

def send_packet(pkt, source="LIVE"):
    """Send packet with source type (LIVE or PCAP)."""
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
    iface = os.getenv("IFACE")
    if iface:
        return iface
    for candidate in ["enp39s0", "ens5", "eth0", "wlan0"]:
        if candidate in get_if_list():
            return candidate
    raise RuntimeError("No suitable network interface found. Available: " + str(get_if_list()))

if __name__ == "__main__":
    time.sleep(3)  # wait for parser/persistor to boot

    if MODE.upper() == "LIVE":
        iface = get_default_iface()
        print(f"🔴 Sniffing live packets on {iface}...")
        sniff(iface=iface, prn=lambda pkt: send_packet(pkt, source="LIVE"))

    else:
        print(f"🔵 Reading from PCAP file: {PCAP_FILE}")
        packets = []
        try:
            packets = rdpcap(PCAP_FILE)
        except Exception as e:
            print(f"⚠️ Failed rdpcap: {e}")
            try:
                with PcapReader(PCAP_FILE) as pcap_reader:
                    packets = [pkt for pkt in pcap_reader]
            except Exception as e2:
                print(f"❌ Could not read {PCAP_FILE}: {e2}")
                packets = []

        print(f"✅ Loaded {len(packets)} packets from {PCAP_FILE}")
        for pkt in packets:
            send_packet(pkt, source="PCAP")
        print("🎉 Finished sending all packets from PCAP.")
