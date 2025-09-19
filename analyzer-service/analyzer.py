import os
import psycopg2
from flask import Flask, jsonify, request
import psycopg2, logging

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

# ✅ Protocol summary for UI
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = "SELECT protocol, COUNT(*) FROM packets GROUP BY protocol"
    logging.debug(f"Running query: {query}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analyzed_packets (
            id SERIAL PRIMARY KEY,
            src_ip VARCHAR(50),
            dst_ip VARCHAR(50),
            protocol VARCHAR(20),
            summary TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()
    # Convert to dict for safe JSON output
    summary_dict = {row[0]: row[1] for row in rows}
    logging.info(f"✅ Retrieved protocol summary: {summary_dict}")
    return jsonify(summary_dict)

# ✅ Get latest packets
@app.route("/packets", methods=["GET"])
def get_packets():
    query = "SELECT id, src_ip, dst_ip, protocol, summary FROM packets ORDER BY id DESC LIMIT 50"
    logging.debug(f"Running query: {query}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    packets = [
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4]}
        for r in rows
    ]
    return jsonify(packets)


@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT protocol, COUNT(*) FROM analyzed_packets GROUP BY protocol;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({row[0]: row[1] for row in rows})


@app.route("/filter", methods=["GET"])
def filter_packets():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify({"error": "Protocol parameter is required"}), 400

    query = "SELECT id, src_ip, dst_ip, protocol, summary FROM packets WHERE protocol=%s ORDER BY id DESC LIMIT 50"
    logging.debug(f"Running query: {query} with protocol={protocol}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, src_ip, dst_ip, protocol, summary, timestamp
        FROM analyzed_packets
        WHERE protocol = %s;
        """,
        (protocol,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    packets = [
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4]}
        for r in rows
    ]
    return jsonify(packets)


@app.route("/health")
def health():
    return "OK", 200


# -------------------------
# Start background processing
# -------------------------
ensure_analyzed_table()
threading.Thread(target=process_packets_loop, daemon=True).start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)

