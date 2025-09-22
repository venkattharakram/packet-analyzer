import os
import psycopg2
from db_config import get_connection
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def init_db():
    conn = get_connection("default")
    cur = conn.cursor()

    # Base table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS packets (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        src_ip VARCHAR(50),
        dst_ip VARCHAR(50),
        protocol VARCHAR(20),
        summary TEXT,
        timestamp TIMESTAMP
    );
    """)

    # Ensure required extra columns exist
    safe_alters = [
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS src_port VARCHAR(10);",
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS dst_port VARCHAR(10);",
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS dns_query TEXT;",
        "ALTER TABLE packets ADD COLUMN IF NOT EXISTS source VARCHAR(10) DEFAULT 'LIVE';"
    ]

    for alter in safe_alters:
        try:
            cur.execute(alter)
        except Exception as e:
            logging.warning(f"Skip alter: {e}")

    conn.commit()
    cur.close()
    conn.close()
    logging.info("✅ Analyzer ensured 'packets' schema is up to date")


if __name__ == "__main__":
    init_db()
