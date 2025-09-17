import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://packetuser:packetpass@db:5432/packetdb")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def ensure_table():
    """Creates the analyzed_packets table if it does not exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analyzed_packets (
            id SERIAL PRIMARY KEY,
            src_ip VARCHAR(50),
            dst_ip VARCHAR(50),
            protocol VARCHAR(20),
            summary TEXT,
            length INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/packets", methods=["GET"])
def get_packets():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, src_ip, dst_ip, protocol, summary, length, timestamp FROM analyzed_packets;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    packets = [
        {
            "id": row[0],
            "src_ip": row[1],
            "dst_ip": row[2],
            "protocol": row[3],
            "summary": row[4],
            "length": row[5],
            "timestamp": row[6].isoformat() if row[6] else None,
        }
        for row in rows
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

    summary = {row[0]: row[1] for row in rows}
    return jsonify(summary)


@app.route("/filter", methods=["GET"])
def filter_packets():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify({"error": "Protocol parameter is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, src_ip, dst_ip, protocol, summary, length, timestamp "
        "FROM analyzed_packets WHERE protocol = %s;",
        (protocol,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    packets = [
        {
            "id": row[0],
            "src_ip": row[1],
            "dst_ip": row[2],
            "protocol": row[3],
            "summary": row[4],
            "length": row[5],
            "timestamp": row[6].isoformat() if row[6] else None,
        }
        for row in rows
    ]
    return jsonify(packets)




if __name__ == "__main__":
    # ❌ Removed ensure_table() from here
    app.run(host="0.0.0.0", port=5003)


@app.route("/health")
def health():
    return "OK", 200

