from flask import Flask, request, jsonify
import psycopg2
import time, logging, sys
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_CONN = "dbname=packetdb user=packetuser password=packetpass host=db port=5432"

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


def get_conn():
    """Create a new DB connection per request"""
    return psycopg2.connect(DB_CONN)


def init_db():
    """Ensure schema exists (only run once)."""
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS packets (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            src_ip VARCHAR(50),
            dst_ip VARCHAR(50),
            protocol VARCHAR(20),
            src_port VARCHAR(10),
            dst_port VARCHAR(10),
            dns_query TEXT,
            summary TEXT,
            timestamp TIMESTAMP,
            source VARCHAR(10) DEFAULT 'LIVE'
        );
        """)
        conn.commit()
        cur.close()
        logging.info("Ensured 'packets' table exists ✅")
    except Exception as e:
        logging.error(f"DB init failed: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()


@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        # Normalize timestamp if in ISO format (2025-09-22T15:50:00)
        ts = pkt.get("timestamp")
        if ts and "T" in ts:
            ts = ts.replace("T", " ")

        cur.execute("""
            INSERT INTO packets
            (src_ip, dst_ip, protocol, src_port, dst_port, dns_query, summary, timestamp, source)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            pkt.get("src_ip"),
            pkt.get("dst_ip"),
            pkt.get("protocol"),
            pkt.get("src_port"),
            pkt.get("dst_port"),
            pkt.get("dns_query"),
            pkt.get("summary"),
            ts,
            pkt.get("source", "LIVE")
        ))

        conn.commit()
        cur.close()
        logging.info(f"Stored packet {pkt.get('protocol')} {pkt.get('src_ip')}->{pkt.get('dst_ip')}")
        return jsonify({"status": "stored"})
    except Exception as e:
        logging.error(f"DB insert failed: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    time.sleep(3)  # wait for DB
    init_db()
    app.run(host="0.0.0.0", port=5002)

