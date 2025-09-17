#!/bin/bash
echo "🛑 Stopping Network Packet Analyzer services..."

# Kill processes by ports
for port in 5000 5001 5002 5003
do
  pid=$(lsof -t -i:$port)
  if [ ! -z "$pid" ]; then
    kill -9 $pid
    echo "Stopped process on port $port (PID $pid)"
  fi
done

# Kill capture-service if running
pid=$(ps aux | grep capture.py | grep -v grep | awk '{print $2}')
if [ ! -z "$pid" ]; then
  kill -9 $pid
  echo "Stopped capture-service (PID $pid)"
fi

echo "✅ All services stopped."
