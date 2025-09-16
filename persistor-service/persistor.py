from flask import Flask, request, jsonify
import psycopg2, time

app = Flask(__name__)

time.sleep(5)
conn = psycopg2.connect(
    dbname="packets", user="admin", password="secret", host="storage-service"
)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS packets (
    id SERIAL PRIMARY KEY,
    src_ip VARCHAR(50),
    dst_ip VARCHAR(50),
    protocol VARCHAR(20),
    src_port VARCHAR(10),
    dst_port VARCHAR(10),
    dns_query TEXT,
    summary TEXT
);
""")
conn.commit()

@app.route("/store", methods=["POST"])
def store_packet():
    pkt = request.json
    cur.execute("""
        INSERT INTO packets (src_ip, dst_ip, protocol, src_port, dst_port, dns_query, summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (pkt["src_ip"], pkt["dst_ip"], pkt["protocol"],
          pkt["src_port"], pkt["dst_port"], pkt["dns_query"], pkt["summary"]))
    conn.commit()
    return jsonify({"status": "stored"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
