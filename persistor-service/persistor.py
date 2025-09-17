from flask import Flask, request, jsonify
import psycopg2
import time
import logging

# -------------------- Setup --------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

# Wait a bit for the DB to be ready
time.sleep(3)

# Database configuration
DB_CONFIG = {
    "dbname": "packetdb",
    "user": "packetuser",
    "password": "packetpass",
    "host": "packet-db",
    "port": 5432
}

# -------------------- DB Helpers --------------------
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        logging.error(f"❌ DB connection failed: {e}")
        raise

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create table if it doesn't exist
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
    logging.info("✅ Table 'packets' ensured")

    # Ensure sequence is synced with max(id)
    cur.execute("""
    SELECT setval(pg_get_serial_sequence('packets','id'), COALESCE((SELECT MAX(id) FROM packets), 1), false);
    """)
    conn.commit()
    logging.info("✅ Sequence 'packets_id_seq' synced with max(id)")

    conn.close()

# Initialize DB on startup
init_db()

# -------------------- Routes --------------------
@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    if not pkt:
        return jsonify({"status": "error", "error": "Empty payload"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
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
        conn.close()
        logging.info(f"✅ Stored packet: {pkt.get('protocol')} from {pkt.get('src_ip')} -> {pkt.get('dst_ip')}")
        return jsonify({"status": "stored"})
    except Exception as e:
        logging.error(f"❌ Failed to store packet: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# -------------------- Main --------------------
if __name__ == "__main__":
    logging.info("🚀 Starting Persistor service on port 5002")
    app.run(host="0.0.0.0", port=5002)
