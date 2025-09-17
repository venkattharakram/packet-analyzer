from flask import Flask, request, jsonify
import psycopg2
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Wait a bit for the DB to be ready
time.sleep(3)

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        dbname="packetdb",
        user="packetuser",
        password="packetpass",
        host="packet-db",  # Docker service name
        port=5432
    )
    cur = conn.cursor()
    logging.info("✅ Connected to PostgreSQL")
except Exception as e:
    logging.error(f"❌ DB connection failed: {e}")
    raise

# Ensure table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS packets (
    id SERIAL PRIMARY KEY,
    src_ip VARCHAR(50),
    dst_ip VARCHAR(50),
    protocol VARCHAR(20),
    src_port VARCHAR(10),
    dst_port VARCHAR(10),
    dns_query TEXT,
    summary TEXT
);
""")
conn.commit()

# Ensure sequence exists and is synced with max id
cur.execute("""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relkind='S' AND relname='packets_id_seq') THEN
        CREATE SEQUENCE packets_id_seq;
        ALTER SEQUENCE packets_id_seq OWNED BY packets.id;
    END IF;
END
$$;
""")
conn.commit()

cur.execute("""
SELECT setval('packets_id_seq', COALESCE((SELECT MAX(id) FROM packets), 0) + 1, false);
""")
conn.commit()
logging.info("✅ Sequence packets_id_seq synced with max(id)")

@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    try:
        cur.execute("""
            INSERT INTO packets (src_ip, dst_ip, protocol, src_port, dst_port, dns_query, summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            pkt.get("src_ip"),
            pkt.get("dst_ip"),
            pkt.get("protocol"),
            pkt.get("src_port"),
            pkt.get("dst_port"),
            pkt.get("dns_query"),
            pkt.get("summary")
        ))
        conn.commit()
        logging.info(f"✅ Stored packet: {pkt.get('protocol')} from {pkt.get('src_ip')} -> {pkt.get('dst_ip')}")
        return jsonify({"status": "stored"})
    except Exception as e:
        logging.error(f"❌ Failed to store packet: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    logging.info("🚀 Starting Persistor service on port 5002")
    app.run(host="0.0.0.0", port=5002)
