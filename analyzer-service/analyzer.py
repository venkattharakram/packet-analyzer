from flask import Flask, jsonify, request
import psycopg2, time, logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

# Wait for DB to be ready
time.sleep(3)

DB_CONFIG = {
    "dbname": "packetdb",
    "user": "packetuser",
    "password": "packetpass",
    "host": "packet-db",
    "port": 5432
}

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("✅ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        raise

# Ensure analyzer table exists and sequence is safe
def ensure_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analyzed_packets (
        id SERIAL PRIMARY KEY,
        src_ip VARCHAR(50),
        dst_ip VARCHAR(50),
        protocol VARCHAR(20),
        summary TEXT,
        analysis_result TEXT
    );
    """)
    conn.commit()

    # Ensure sequence exists and synced
    cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname='analyzed_packets_id_seq') THEN
            CREATE SEQUENCE analyzed_packets_id_seq;
            ALTER SEQUENCE analyzed_packets_id_seq OWNED BY analyzed_packets.id;
            SELECT setval('analyzed_packets_id_seq', COALESCE((SELECT MAX(id) FROM analyzed_packets), 0));
        END IF;
    END
    $$;
    """)
    conn.commit()
    conn.close()

ensure_table()

# ✅ Protocol summary for UI
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = "SELECT protocol, COUNT(*) FROM analyzed_packets GROUP BY protocol"
    logging.debug(f"Running query: {query}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    summary_dict = {row[0]: row[1] for row in rows}
    logging.info(f"✅ Retrieved protocol summary: {summary_dict}")
    return jsonify(summary_dict)

# ✅ Get latest analyzed packets
@app.route("/packets", methods=["GET"])
def get_packets():
    query = "SELECT id, src_ip, dst_ip, protocol, summary, analysis_result FROM analyzed_packets ORDER BY id DESC LIMIT 50"
    logging.debug(f"Running query: {query}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    packets = [
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4], "analysis_result": r[5]}
        for r in rows
    ]
    logging.info(f"✅ Retrieved {len(packets)} packets")
    return jsonify(packets)

# ✅ Filter packets by protocol
@app.route("/filter", methods=["GET"])
def filter_by_protocol():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify([])

    query = "SELECT id, src_ip, dst_ip, protocol, summary, analysis_result FROM analyzed_packets WHERE protocol=%s ORDER BY id DESC LIMIT 50"
    logging.debug(f"Running query: {query} with protocol={protocol}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (protocol,))
    rows = cur.fetchall()
    conn.close()
    packets = [
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4], "analysis_result": r[5]}
        for r in rows
    ]
    logging.info(f"✅ Retrieved {len(packets)} packets for protocol {protocol}")
    return jsonify(packets)

if __name__ == "__main__":
    logging.info("🚀 Starting Analyzer service on port 5003")
    app.run(host="0.0.0.0", port=5003)
