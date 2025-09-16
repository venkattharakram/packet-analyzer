# Network Packet Analyzer

Microservices project to sniff live packets or read from PCAP files, parse & classify them, store in PostgreSQL, analyze summaries, and visualize via UI.

## Sample PCAPs
Run this to download example capture files into `sample-pcaps/`:

```bash
python3 sample-pcaps/fetch_pcaps.py
```

Then start the stack:

```bash
docker-compose up --build
```
#
# Network Packet Analysis and Protocol Classification

## 📌 Overview
This project is a **microservices-based network packet analyzer**.  
It captures, parses, stores, analyzes, and visualizes network traffic.  
The architecture is split into **five microservices**: Capture, Parser, Persistor, Analyzer, and UI.

---

## 🏗️ Architecture

```
Capture → Parser → Persistor → PostgreSQL ← Analyzer ← UI
```

- **Capture Service**  
  Sniffs live packets or replays `.pcap` files → sends JSON to Parser.

- **Parser Service**  
  Classifies packets (TCP, UDP, ICMP, DNS, etc.) → forwards JSON to Persistor.

- **Persistor Service**  
  Inserts packets into PostgreSQL `packets` table.

- **Analyzer Service**  
  Queries PostgreSQL → exposes APIs (`/protocol_summary`, `/packets`, `/filter`).

- **UI Service**  
  Calls Analyzer APIs → displays results in a browser dashboard.

---

## ⚙️ Data Flow

1. **Capture**  
   - Input: Network interface (`enp39s0`) or `.pcap` file.  
   - Output: Sends JSON to Parser.  
   - Storage: ❌ No storage.  
   - Stops automatically after PCAP replay OR runs forever in live mode.

2. **Parser**  
   - Input: JSON from Capture (`/parse`).  
   - Output: Sends classified JSON to Persistor.  
   - Storage: ❌ No storage.  
   - Runs continuously on port `5001`.

3. **Persistor**  
   - Input: JSON from Parser (`/store`).  
   - Output: Inserts into PostgreSQL.  
   - Storage: ✅ Yes, in DB.  
   - Runs continuously on port `5002`.

4. **Analyzer**  
   - Input: Reads from PostgreSQL.  
   - Output: Provides summary & packet APIs to UI.  
   - Storage: ❌ No storage.  
   - Runs continuously on port `5003`.

5. **UI**  
   - Input: Calls Analyzer APIs.  
   - Output: Renders dashboard (protocol summary + packets table).  
   - Storage: ❌ No storage.  
   - Runs continuously on port `5000`.

---

## 📝 Logs

- **capture.log** → Sniffing start/stop, parser errors.  
- **parser.log** → Received packets, persistor errors.  
- **persistor.log** → DB inserts, errors.  
- **analyzer.log** → SQL queries, results, API calls.  
- **ui.log** → Page requests, UI access logs.  

---

## 🚀 Running the Project

### Prerequisites
- Python 3.9+  
- PostgreSQL installed & running  
- Required Python packages: `Flask`, `psycopg2`, `scapy`, `requests`

### Steps

1. Clone the repo:
   ```bash
   git clone https://github.com/your-org/packet-analyzer.git
   cd packet-analyzer
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Start PostgreSQL and create DB:
   ```bash
   createdb packets
   psql -d packets -c "CREATE TABLE packets (id SERIAL PRIMARY KEY, src_ip TEXT, dst_ip TEXT, protocol TEXT, summary TEXT);"
   ```

4. Run all services:
   ```bash
   ./run_all.sh
   ```

   - Choose `1` for PCAP replay OR `2` for live sniffing.  
   - Logs will be written under `logs/`.

5. Access the UI in browser:
   ```
   http://<EC2-PUBLIC-IP>:5000
   ```

---

## 🔎 Example Traffic

To generate traffic on your EC2:
```bash
ping -c 3 8.8.8.8
curl http://google.com
```

These will appear in the dashboard as ICMP, TCP, and DNS packets.

---

## 📂 Microservices Documentation

Each microservice has its own README for detailed explanation:
- [Capture Service](capture-service-README.md)  
- [Parser Service](parser-service-README.md)  
- [Persistor Service](persistor-service-README.md)  
- [Analyzer Service](analyzer-service-README.md)  
- [UI Service](ui-service-README.md)  

---

## ✅ Summary

- Data is **never stored as JSON files**.  
- JSON is used only for **communication between services**.  
- Final storage is in **PostgreSQL `packets` table**.  
- The system supports both **live sniffing** and **PCAP replay**.  
