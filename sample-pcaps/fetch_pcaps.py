#!/usr/bin/env python3
import os, sys
import urllib.request

PCAPS = {
    "dns.cap": "https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/dns.cap",
    "http.cap": "https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/http.cap",
    "tcp-udp-icmp.pcap": "https://wiki.wireshark.org/uploads/__moin_import__/attachments/SampleCaptures/tcp-udp-icmp.pcap",
}

def download(url, path):
    print(f"Downloading {url} -> {path}")
    urllib.request.urlretrieve(url, path)

def main():
    os.makedirs("sample-pcaps", exist_ok=True)
    for fname, url in PCAPS.items():
        path = os.path.join("sample-pcaps", fname)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"[skip] {fname} already exists")
            continue
        try:
            download(url, path)
            print(f"[ok] {fname}")
        except Exception as e:
            print(f"[error] {fname}: {e}")
            print("Please download manually if needed.")
    print("Done.")

if __name__ == "__main__":
    main()
