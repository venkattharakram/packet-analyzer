from flask import Flask, request, jsonify
import psycopg2, time

app = Flask(__name__)
time.sleep(5)

conn = psycopg2.connect(
    dbname="packets", user="admin", password="secret", host="storage-service"
)
cur = conn.cursor()

@app.route("/packets", methods=["GET"])
def get_packets():
    cur.execute("SELECT id, src_ip, dst_ip, protocol, summary FROM packets LIMIT 20")
    rows = cur.fetchall()
    return jsonify(rows)

@app.route("/summary", methods=["GET"])
def get_summary():
    cur.execute("SELECT protocol, COUNT(*) FROM packets GROUP BY protocol")
    rows = cur.fetchall()
    return jsonify({r[0]: r[1] for r in rows})

@app.route("/filter", methods=["GET"])
def filter_protocol():
    proto = request.args.get("protocol")
    cur.execute("SELECT id, src_ip, dst_ip, summary FROM packets WHERE protocol=%s LIMIT 20", (proto,))
    rows = cur.fetchall()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
