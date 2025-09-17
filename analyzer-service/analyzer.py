import os
import psycopg2
from flask import Flask, jsonify, request
import threading
import time
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://packetuser:packetpass@db:5432/packetdb"
)

# -------------------------
# Database utilities
# -------------------------
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def ensure_analyzed_table():
    """Creates the analyzed_packets table if it does not exist."""
    conn = get_db_connection()
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


# -------------------------
# Background analyzer loop
# -------------------------
def process_packets_loop(interval=1):
    """Continuously process new packets from the packets table."""
    while True:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Fetch unprocessed packets
            cur.execute(
                """
                SELECT id, src_ip, dst_ip, protocol, summary
                FROM packets
                WHERE id NOT IN (SELECT id FROM analyzed_packets)
                ORDER BY id ASC
                LIMIT 50;
                """
            )
            rows = cur.fetchall()
            for row in rows:
                cur.execute(
                    """
                    INSERT INTO analyzed_packets (id, src_ip, dst_ip, protocol, summary, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (*row, datetime.utcnow()),
                )
            conn.commit()
            cur.close()
            conn.close()
            if rows:
                print(f"✅ Processed {len(rows)} packet(s)")
        except Exception as e:
            print(f"[Analyzer Loop Error] {e}")
        time.sleep(interval)


# -------------------------
# Flask API endpoints
# -------------------------
@app.route("/packets", methods=["GET"])
def get_packets():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, src_ip, dst_ip, protocol, summary, timestamp FROM analyzed_packets;"
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
            "timestamp": row[5].isoformat() if row[5] else None,
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
    return jsonify({row[0]: row[1] for row in rows})


@app.route("/filter", methods=["GET"])
def filter_packets():
    protocol = request.args.get("protocol")
    if not protocol:
        return jsonify({"error": "Protocol parameter is required"}), 400

    conn = get_db_connection()
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
        {
            "id": row[0],
            "src_ip": row[1],
            "dst_ip": row[2],
            "protocol": row[3],
            "summary": row[4],
            "timestamp": row[5].isoformat() if row[5] else None,
        }
        for row in rows
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

