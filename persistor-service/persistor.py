from flask import Flask, request, jsonify
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

@app.route("/store", methods=["POST"])
def store_packet():
    data = request.json
    src_ip = data.get("src_ip", "unknown")
    dst_ip = data.get("dst_ip", "unknown")
    protocol = data.get("protocol", "unknown")
    summary = data.get("raw", "")
    source = data.get("source", "LIVE")  # ✅ Default LIVE if not given

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO packets (src_ip, dst_ip, protocol, summary, timestamp, source)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (src_ip, dst_ip, protocol, summary, source))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(f"❌ DB Insert failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info("🚀 Starting Persistor service on port 5002")
    app.run(host="0.0.0.0", port=5002)
