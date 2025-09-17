from flask import Flask, request, jsonify
import psycopg2
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

# Wait a bit for DB to be ready
time.sleep(3)

# ----------------- Connect to PostgreSQL -----------------
try:
    conn = psycopg2.connect(
        dbname="packetdb",
        user="packetuser",
        password="packetpass",
        host="packet-db",  # Docker service name
        port=5432
    )
    cur = conn.cursor()
    logging.info("✅ Connected to PostgreSQL database")
except Exception as e:
    logging.error(f"❌ DB connection failed: {e}")
    raise

# ----------------- DB Initialization -----------------
def ensure_table():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analyzed_packets (
        id SERIAL PRIMARY KEY,
        src_ip VARCHAR(50),
        dst_ip VARCHAR(50),
        protocol VARCHAR(20),
        src_port VARCHAR(10),
        dst_port VARCHAR(10),
        summary TEXT
    );
    """)
    conn.commit()
    logging.info("✅ Table 'analyzed_packets' ensured")

    # Safely sync the sequence only if it exists
    try:
        cur.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_class WHERE relname='analyzed_packets_id_seq') THEN
                PERFORM setval('analyzed_packets_id_seq', COALESCE((SELECT MAX(id) FROM analyzed_packets), 1), true);
            END IF;
        END
        $$;
        """)
        conn.commit()
        logging.info("✅ Sequence 'analyzed_packets_id_seq' synced safely")
    except Exception as e:
        logging.warning(f"⚠ Could not sync sequence: {e}")
        conn.rollback()

ensure_table()
# -----------------------------------------------------

@app.route("/analyze", methods=["POST"])
def analyze_packet():
    pkt = request.json
    summary = f"{pkt.get('protocol')} packet from {pkt.get('src_ip')} to {pkt.get('dst_ip')}"
    try:
        cur.execute("""
            INSERT INTO analyzed_packets (src_ip, dst_ip, protocol, src_port, dst_port, summary)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            pkt.get("src_ip"),
            pkt.get("dst_ip"),
            pkt.get("protocol"),
            pkt.get("src_port"),
            pkt.get("dst_port"),
            summary
        ))
        conn.commit()
        logging.info(f"✅ Analyzed packet stored: {summary}")
        return jsonify({"status": "analyzed", "summary": summary})
    except Exception as e:
        logging.error(f"❌ Failed to analyze packet: {e}")
        conn.rollback()
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    logging.info("🚀 Starting Analyzer service on port 5003")
    app.run(host="0.0.0.0", port=5003)

