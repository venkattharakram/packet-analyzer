from flask import Flask, request, jsonify
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

@app.route("/store", methods=["POST"])
def store_packet():
    data = request.json
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO packets (src_ip, dst_ip, protocol, summary, timestamp, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get("src_ip"),
            data.get("dst_ip"),
            data.get("protocol"),
            data.get("raw"),
            data.get("timestamp"),
            data.get("source", "LIVE")
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(f"Persistor error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logging.info("🚀 Starting Persistor service on port 5002")
    app.run(host="0.0.0.0", port=5002)
