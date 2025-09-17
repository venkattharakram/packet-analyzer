from flask import Flask, request, jsonify
import psycopg2, time
from datetime import datetime

app = Flask(__name__)

# Wait a little in case DB needs to be ready
time.sleep(3)

# Connect to local PostgreSQL (running on localhost)
conn = psycopg2.connect(
    dbname="packets",
    user="admin",
    password="secret",
    host="localhost",   # using local DB
    port=5432
)
cur = conn.cursor()

# Ensure table exists (now with timestamp)
cur.execute("""
CREATE TABLE IF NOT EXISTS packets (
    id SERIAL PRIMARY KEY,
    src_ip VARCHAR(50),
    dst_ip VARCHAR(50),
    protocol VARCHAR(20),
    src_port VARCHAR(10),
    dst_port VARCHAR(10),
    dns_query TEXT,
    summary TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    cur.execute("""
        INSERT INTO packets (src_ip, dst_ip, protocol, src_port, dst_port, dns_query, summary, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        pkt.get("src_ip"),
        pkt.get("dst_ip"),
        pkt.get("protocol"),
        pkt.get("src_port"),
        pkt.get("dst_port"),
        pkt.get("dns_query"),
        pkt.get("summary"),
        datetime.utcnow()   # always store UTC timestamp
    ))
    conn.commit()
    return jsonify({"status": "stored"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
