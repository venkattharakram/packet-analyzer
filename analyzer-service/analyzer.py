from flask import Flask, jsonify, request
import psycopg2, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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
        logging.info("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        raise

# --- Protocol summary grouped by protocol + source ---
@app.route("/protocol_summary", methods=["GET"])
def protocol_summary():
    query = """
    SELECT protocol, 
           COALESCE(source, 'UNKNOWN') as source, 
           COUNT(*) 
    FROM packets 
    GROUP BY protocol, source
    """
    try:
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
    except Exception as e:
        logging.error(f"Error in /protocol_summary: {e}")
        return jsonify({"error": str(e)}), 500

# --- Get packets (optionally by source) ---
@app.route("/packets", methods=["GET"])
def get_packets():
    source = request.args.get("source")  # optional
    base_query = "SELECT id, src_ip, dst_ip, protocol, summary, timestamp, source FROM packets"
    query = base_query + " ORDER BY id DESC LIMIT 50"
    params = ()

    if source:
        query = base_query + " WHERE source=%s ORDER BY id DESC LIMIT 50"
        params = (source,)

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
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
                "source": r[6] if len(r) > 6 else "UNKNOWN"
            }
            for r in rows
        ]
        return jsonify(packets)
    except Exception as e:
        logging.error(f"Error in /packets: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info("🚀 Starting Analyzer service on port 5003")
    app.run(host="0.0.0.0", port=5003)
