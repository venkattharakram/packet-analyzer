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
