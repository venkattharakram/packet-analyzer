from scapy.all import sniff, rdpcap, get_if_list
import requests, time, os

MODE = os.getenv("MODE", "PCAP")        # MODE=LIVE or PCAP
PCAP_FILE = os.getenv("PCAP_FILE", "sample-pcaps/dns.cap")  # fallback
PARSER_URL = "http://127.0.0.1:5001/parse"

def send_packet(pkt):
    data = {"raw": pkt.summary(), "hex": bytes(pkt).hex()}
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

def read_pcap(file_path):
    """Try reading PCAP, if it fails try PCAPNG"""
    try:
        return rdpcap(file_path)
    except Exception as e:
        print(f"⚠️ Failed to read with rdpcap: {e}")
        try:
            from scapy.utils import PcapNgReader
            packets = []
            with PcapNgReader(file_path) as pcapng:
                for pkt in pcapng:
                    packets.append(pkt)
            return packets
        except Exception as e2:
            print(f"❌ Could not read {file_path} as PCAP or PCAPNG: {e2}")
            return []

if __name__ == "__main__":
    time.sleep(3)

    if MODE.upper() == "LIVE":
        iface = get_default_iface()
        print(f"🔴 Sniffing live packets on {iface}... (press Ctrl+C to stop)")
        sniff(iface=iface, prn=send_packet)  # no count, runs until stopped
    else:
        print(f"🔵 Reading from PCAP file: {PCAP_FILE}")
        packets = read_pcap(PCAP_FILE)
        print(f"✅ Loaded {len(packets)} packets from {PCAP_FILE}")
        for idx, pkt in enumerate(packets, start=1):
            send_packet(pkt)
            if idx % 100 == 0:
                print(f"📦 Sent {idx} packets...")
        print("🎉 Finished sending all packets from PCAP.")
