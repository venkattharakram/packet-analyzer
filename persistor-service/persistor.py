from flask import Flask, request, jsonify
import psycopg2, time, logging, sys

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_CONN = "dbname=packetdb user=packetuser password=packetpass host=db port=5432"

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

time.sleep(3)  # wait for DB

# Connect to Postgres (hardcoded)
try:
    conn = psycopg2.connect("dbname=packetdb user=packetuser password=packetpass host=db port=5432")
    cur = conn.cursor()
    logging.info("Connected to Postgres ✅")
except Exception as e:
    logging.error(f"Failed to connect to DB: {e}")
    sys.exit(1)


def init_db():
    """Ensure schema exists (only run once)."""
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
    logging.info("Ensured 'packets' table exists ✅")


@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    cur.execute("""
        INSERT INTO packets (src_ip, dst_ip, protocol, src_port, dst_port, dns_query, summary, timestamp, source)
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


if __name__ == "__main__":
    # Run schema creation only once (not in every Gunicorn worker)
    init_db()
    app.run(host="0.0.0.0", port=5002)
