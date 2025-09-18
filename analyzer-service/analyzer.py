from flask import Flask, jsonify, request
import psycopg2, logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        dbname="packets",
        user="admin",
        password="secret",
        host="127.0.0.1",
        port=5432
    )

# ✅ Protocol summary grouped by protocol + source
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = "SELECT protocol, source, COUNT(*) FROM packets GROUP BY protocol, source"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    summary = {}
    for protocol, source, count in rows:
        if protocol not in summary:
            summary[protocol] = {}
        summary[protocol][source] = count
    return jsonify(summary)

# ✅ Get latest packets (optionally by source)
@app.route("/packets", methods=["GET"])
def get_packets():
    source = request.args.get("source")
    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets"
    if source:
        query += " WHERE source=%s ORDER BY id DESC LIMIT 50"
    else:
        query += " ORDER BY id DESC LIMIT 50"

    conn = get_connection()
    cur = conn.cursor()
    if source:
        cur.execute(query, (source,))
    else:
        cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    packets = [
        {
            "id": r[0],
            "src_ip": r[1],
            "dst_ip": r[2],
            "protocol": r[3],
            "summary": r[4],
            "timestamp": r[5].isoformat() if r[5] else None,
            "source": r[6]
        }
        for r in rows
    ]
    return jsonify(packets)

# ✅ Filter packets by protocol (UI depends on this!)
@app.route("/filter", methods=["GET"])
def filter_by_protocol():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify([])

    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets WHERE protocol=%s ORDER BY id DESC LIMIT 50"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (protocol,))
    rows = cur.fetchall()
    conn.close()

    packets = [
        {
            "id": r[0],
            "src_ip": r[1],
            "dst_ip": r[2],
            "protocol": r[3],
            "summary": r[4],
            "timestamp": r[5].isoformat() if r[5] else None,
            "source": r[6]
        }
        for r in rows
    ]
    return jsonify(packets)

# ✅ Get all protocols traffic (for UI "All Protocols" button)
@app.route("/all_protocols", methods=["GET"])
def all_protocols():
    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets ORDER BY id DESC LIMIT 200"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    packets = [
        {
            "id": r[0],
            "src_ip": r[1],
            "dst_ip": r[2],
            "protocol": r[3],
            "summary": r[4],
            "timestamp": r[5].isoformat() if r[5] else None,
            "source": r[6]
        }
        for r in rows
    ]
    return jsonify(packets)

if __name__ == "__main__":
    logging.info("🚀 Starting Analyzer service on port 5003")
    app.run(host="0.0.0.0", port=5003)
