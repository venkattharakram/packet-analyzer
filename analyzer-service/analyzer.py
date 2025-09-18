from flask import Flask, jsonify, request
import psycopg2, logging, os

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

# ✅ Latest packets
@app.route("/packets", methods=["GET"])
def get_packets():
    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp FROM packets ORDER BY id DESC LIMIT 50"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4],
         "timestamp": r[5].isoformat() if r[5] else None}
        for r in rows
    ])

# ✅ Filter packets
@app.route("/filter", methods=["GET"])
def filter_by_protocol():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify([])
    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp FROM packets WHERE protocol=%s ORDER BY id DESC LIMIT 50"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, (protocol,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4],
         "timestamp": r[5].isoformat() if r[5] else None}
        for r in rows
    ])

# ✅ All protocols (no filter)
@app.route("/all_packets", methods=["GET"])
def all_packets():
    query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp FROM packets ORDER BY id DESC LIMIT 200"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "src_ip": r[1], "dst_ip": r[2], "protocol": r[3], "summary": r[4],
         "timestamp": r[5].isoformat() if r[5] else None}
        for r in rows
    ])

# ✅ Mode info
@app.route("/mode", methods=["GET"])
def get_mode():
    try:
        with open("logs/mode.info", "r") as f:
            mode = f.read().strip()
    except:
        mode = "Unknown"
    return jsonify({"mode": mode})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
