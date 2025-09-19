#!/bin/bash
echo "Stopping old services if running..."
./stop.sh

echo "Starting all services..."

# Start Capture (idle, will wait for UI Start Sniffing request)
nohup python3 capture_service.py > logs/capture.log 2>&1 &

# Start Parser
nohup python3 parser_service.py > logs/parser.log 2>&1 &

# Start Persistor
nohup python3 persistor_service.py > logs/persistor.log 2>&1 &

# Start Analyzer
nohup python3 analyzer_service.py > logs/analyzer.log 2>&1 &

# Start UI
cd ui && nohup npm start > ../logs/ui.log 2>&1 &
