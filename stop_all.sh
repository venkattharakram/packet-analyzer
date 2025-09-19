#!/bin/bash
echo "🛑 Stopping Network Packet Analyzer services..."

# Kill services by ports (UI, Parser, Persistor, Analyzer)
for port in 5000 5001 5002 5003
do
  pid=$(lsof -t -i:$port 2>/dev/null)
  if [ ! -z "$pid" ]; then
    kill -9 $pid 2>/dev/null || sudo kill -9 $pid
    echo "Stopped process on port $port (PID $pid)"
  fi
done

# Kill capture-service (both ec2-user and root)
sudo pkill -f "capture-service/capture.py" 2>/dev/null
if [ $? -eq 0 ]; then
  echo "Stopped capture-service"
fi

echo "✅ All services stopped."
