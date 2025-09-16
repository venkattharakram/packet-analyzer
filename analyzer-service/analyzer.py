from flask import Flask, jsonify, request
import psycopg2
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="packets",
            user="admin",
            password="secret",
            host="127.0.0.1",
            port=5432
        )
        logging.info("✅ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        raise

# ✅ Matches UI (protocol summary)
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = "SELECT protocol, COUNT(*) FROM packets GROUP BY protocol"
    logging.debug(f"Running query: {query}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    logging.info(f"✅ Retrieved protocol summary: {rows}")
    return jsonify(rows)

# ✅ Matches UI (packets table)
@app.route("/packets", methods=["GET"])
def get_packets():
    query = "SELECT id, src_ip, dst_ip, protocol, summary FROM packets ORDER BY id DESC LIMIT 50"
    logging.debug(f"Running query: {query}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    logging.info(f"✅ Retrieved {len(rows)} packets")
    return jsonify(rows)

# ✅ New endpoint for filtering by protocol
@app.route("/filter", methods=["GET"])
def filter_by_protocol():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify([])

    query = "SELECT id, src_ip, dst_ip, protocol, summary FROM packets WHERE protocol=%s ORDER BY id DESC LIMIT 50"
    logging.debug(f"Running query: {query} with protocol={protocol}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (protocol,))
    rows = cur.fetchall()
    conn.close()
    logging.info(f"✅ Retrieved {len(rows)} packets for protocol {protocol}")
    return jsonify(rows)

if __name__ == "__main__":
    logging.info("🚀 Starting Analyzer service on port 5003")
    app.run(host="0.0.0.0", port=5003)
