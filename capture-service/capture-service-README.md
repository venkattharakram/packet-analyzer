# Capture Service — README

## Overview
The Capture Service is responsible for **sniffing network packets** (live or from `.pcap` files) using **Scapy**.  
It does **not store data**. Instead, it forwards each packet to the Parser Service.

## Data Flow
- **Input**:  
  - Live packets from EC2 network interface (e.g., `enp39s0`)  
  - Or replayed packets from `.pcap` files  
- **Output**:  
  - Sends JSON data (packet metadata) to **Parser Service**:  
    ```
    POST http://127.0.0.1:5001/parse
    ```
- **Storage**:  
  - ❌ No storage (only forwards packets).

## Lifecycle
- In **PCAP replay mode** → stops automatically once all packets in the file are read.  
- In **LIVE sniffing mode** → runs continuously until manually stopped (`CTRL+C` or `pkill`).  

## Logs
- **capture.log** shows:  
  - Interface being sniffed (`🔴 Sniffing live packets on enp39s0...`)  
  - Errors if Parser is unreachable (`Error sending to parser ...`)  
- ❌ It does not log every single packet (too heavy). Only summaries/errors.
