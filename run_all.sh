#!/bin/bash
echo "🚀 Starting Network Packet Analyzer services..."

# Kill any old processes first
./stop_all.sh

# Create logs folder if missing
mkdir -p logs

# Start Persistor (port 5002)
nohup python3 persistor-service/persistor.py > logs/persistor.log 2>&1 &
echo "✅ Persistor started on port 5002"

# Start Parser (port 5001)
nohup python3 parser-service/parser.py > logs/parser.log 2>&1 &
echo "✅ Parser started on port 5001"

# Start Analyzer (port 5003)
nohup python3 analyzer-service/analyzer.py > logs/analyzer.log 2>&1 &
echo "✅ Analyzer started on port 5003"

# Start UI (port 5000)
nohup python3 ui-service/app.py > logs/ui.log 2>&1 &
echo "✅ UI started on port 5000 (http://<EC2-PUBLIC-IP>:5000)"

# Ask user for capture mode
echo "Choose capture mode:"
echo "1) PCAP replay (default dns.cap)"
echo "2) LIVE sniffing (requires sudo)"
read -p "Enter choice [1 or 2]: " choice

if [ "$choice" == "2" ]; then
    echo "🔴 Running in LIVE mode (sniffing eth0)"
   # nohup sudo MODE=LIVE python3 capture-service/capture.py > logs/capture.log 2>&1 &
    nohup sudo MODE=LIVE python3 capture-service/capture.py &> logs/capture.log  &
else
    echo "🔵 Running in PCAP mode (sample-pcaps/dns.cap)"
    nohup MODE=PCAP python3 capture-service/capture.py > logs/capture.log 2>&1 &
fi

echo "🎉 All services are running! Check logs/ folder for details."
                           
