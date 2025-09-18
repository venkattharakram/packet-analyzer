from scapy.all import sniff, rdpcap, get_if_list
from scapy.utils import PcapReader
import requests, time, os, json
from datetime import datetime

# Mode & file inputs
MODE = os.getenv("MODE", "PCAP")        # MODE=LIVE or PCAP
PCAP_FILE = os.getenv("PCAP_FILE", "sample-pcaps/dns.cap")  # take from env, fallback to dns.cap

# Parser service endpoint
#PARSER_URL = "http://parser-service:5001/parse"
PARSER_URL = "http://127.0.0.1:5001/parse"

# File where we save last PCAP info
STATUS_FILE = "logs/last_pcap.json"

def send_packet(pkt):
    """Send packet summary + raw hex to parser service"""
    data = {"raw": pkt.summary(), "hex": bytes(pkt).hex()}
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
        # ---- Live sniffing ----
        iface = get_default_iface()
        print(f"🔴 Sniffing live packets on {iface}...")
        sniff(iface=iface, prn=send_packet)  # no count limit → will run until stopped

    else:
        # ---- PCAP replay ----
        print(f"🔵 Reading from PCAP file: {PCAP_FILE}")
        packets = []
        try:
            # Try rdpcap first
            packets = rdpcap(PCAP_FILE)
        except Exception as e:
            print(f"⚠️ Failed to read with rdpcap: {e}")
            try:
                # Try PcapReader as fallback
                with PcapReader(PCAP_FILE) as pcap_reader:
                    packets = [pkt for pkt in pcap_reader]
            except Exception as e2:
                print(f"❌ Could not read {PCAP_FILE} as PCAP or PCAPNG: {e2}")
                packets = []

        print(f"✅ Loaded {len(packets)} packets from {PCAP_FILE}")
        for pkt in packets:
            send_packet(pkt)

        # Save info for UI
        try:
            os.makedirs("logs", exist_ok=True)
            with open(STATUS_FILE, "w") as f:
                json.dump({
                    "file": PCAP_FILE,
                    "count": len(packets),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }, f)
        except Exception as e:
            print("⚠️ Could not write PCAP status file:", e)

        print("🎉 Finished sending all packets from PCAP.")
