from flask import Flask, request, jsonify
import psycopg2, logging, sys, time
from db_config import get_connection  # ✅ central DB config

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

# Wait a bit for DB container to be ready
time.sleep(3)

# ✅ Connect to DB using shared config
try:
    conn = get_connection("default")   # packetdb / packetuser
    cur = conn.cursor()
    logging.info("Connected to Postgres ✅")
except Exception as e:
    logging.error(f"Failed to connect to DB: {e}")
    sys.exit(1)


def init_db():
    """Ensure schema & columns exist (idempotent)."""
    cur.execute("""
    CREATE TABLE IF NOT EXISTS packets (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        src_ip VARCHAR(50),
        dst_ip VARCHAR(50),
        protocol VARCHAR(20),
        summary TEXT,
        timestamp TIMESTAMP
    );
    """)

    # Ensure all required columns exist
    safe_alters = [
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS src_port VARCHAR(10);",
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS dst_port VARCHAR(10);",
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS dns_query TEXT;",
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS source VARCHAR(10) DEFAULT 'LIVE';"
    ]
    for alter in safe_alters:
        try:
            cur.execute(alter)
        except Exception as e:
            logging.warning(f"Skip alter: {e}")

    conn.commit()
    logging.info("✅ Ensured 'packets' schema is up to date")


@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    try:
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
            pkt.get("timestamp"),
            pkt.get("source", "LIVE")
        ))
        conn.commit()
        logging.info(f"Stored packet {pkt.get('protocol')} {pkt.get('src_ip')}->{pkt.get('dst_ip')}")
        return jsonify({"status": "stored"})
    except Exception as e:
        conn.rollback()
        logging.error(f"❌ Failed to insert packet: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    init_db()  # auto-fix schema at startup
    app.run(host="0.0.0.0", port=5002)