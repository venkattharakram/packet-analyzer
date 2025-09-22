# db_init.py
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://packetuser:packetpass@db:5432/packetdb")


def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Create the table only once
    cur.execute("""
        CREATE TABLE IF NOT EXISTS packets (
        id SERIAL PRIMARY KEY,
        src_ip VARCHAR(50),
        dst_ip VARCHAR(50),
        protocol VARCHAR(20),
        src_port VARCHAR(10),
        dst_port VARCHAR(10),
        dns_query TEXT,
        summary TEXT,
        timestamp TIMESTAMP,
        source VARCHAR(10) DEFAULT 'LIVE'
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ analyzed_packets table ensured")


if __name__ == "__main__":
    init_db()

