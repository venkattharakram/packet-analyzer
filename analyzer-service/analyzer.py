from flask import Flask, jsonify, request
import psycopg2, logging

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        dbname="packets",
        user="admin",
        password="secret",
        host="127.0.0.1",
        port=5432
    )

# ✅ Protocol summary
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = "SELECT protocol, COUNT(*) FROM packets GROUP BY protocol"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return jsonify({row[0]: row[1] for row in rows})

# ✅ Get packets (with optional source filter)
@app.route("/packets", methods=["GET"])
def get_packets():
    source = request.args.get("source")  # LIVE / PCAP / None
    base_query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets"
    params = []

    if source:
        base_query += " WHERE source=%s"
        params.append(source)

    base_query += " ORDER BY id DESC LIMIT 50"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(base_query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    packets = [
        {
            "id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3],
            "summary": r[4], "timestamp": r[5].isoformat() if r[5] else None,
            "source": r[6]
        } for r in rows
    ]
    return jsonify(packets)

# ✅ Filter by protocol
@app.route("/filter", methods=["GET"])
def filter_by_protocol():
    protocol = request.args.get("protocol")
    source = request.args.get("source")  # Optional source filter
    if not protocol:
        return jsonify([])

    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets WHERE protocol=%s"
    params = [protocol]

    if source:
        query += " AND source=%s"
        params.append(source)

    query += " ORDER BY id DESC LIMIT 50"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    conn.close()

    packets = [
        {
            "id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3],
            "summary": r[4], "timestamp": r[5].isoformat() if r[5] else None,
            "source": r[6]
        } for r in rows
    ]
    return jsonify(packets)

if __name__ == "__main__":
    logging.info("🚀 Starting Analyzer service on port 5003")
    app.run(host="0.0.0.0", port=5003)
