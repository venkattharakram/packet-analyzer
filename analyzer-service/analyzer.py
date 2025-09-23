from flask import Flask, jsonify, request
import psycopg2,logging
from db_config import get_connection  # ✅ Import from your shared config

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
app = Flask(__name__)

# ✅ Protocol summary (grouped by protocol & source)
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = "SELECT protocol, source, COUNT(*) FROM packets GROUP BY protocol, source"
    conn = get_connection("default")   # uses packetdb / packetuser by default
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

# ✅ Get packets (optionally by source)
@app.route("/packets", methods=["GET"])
def get_packets():
    source = request.args.get("source")
    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets"
    if source:
        query += " WHERE source=%s ORDER BY id DESC LIMIT 50"
    else:
        query += " ORDER BY id DESC LIMIT 50"

    conn = get_connection("default")
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

# ✅ Filter packets by protocol
@app.route("/filter", methods=["GET"])
def filter_by_protocol():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify([])

    query = """SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source
               FROM packets WHERE protocol=%s ORDER BY id DESC LIMIT 50"""
    conn = get_connection("default")
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

# ✅ All protocols (detailed list, not counts)
@app.route("/all_protocols", methods=["GET"])
def all_protocols():
    query = """SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source
               FROM packets ORDER BY id DESC LIMIT 200"""
    conn = get_connection("default")
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

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)