import os
import socket

def detect_host():
    """
    Detect whether we are running inside Docker Compose or on host.
    - If running inside Docker Compose, DB_HOST should be 'packets-db'
    - If running on EC2 host, DB_HOST should default to 'localhost'
    """
    db_host = os.getenv("DB_HOST")
    if db_host:
        return db_host

    try:
        socket.gethostbyname("db")
        return "db"
    except socket.gaierror:
        return "localhost"


# Define multiple DB configs
DATABASES = {
    "default": {
        "dbname": os.getenv("DB_NAME", "packetdb"),
        "user": os.getenv("DB_USER", "packetuser"),
        "password": os.getenv("DB_PASS", "packetpass"),
        "host": detect_host(),
        "port": os.getenv("DB_PORT", "5432"),
    },
    "admin_db": {
        "dbname": os.getenv("ADMIN_DB_NAME", "packets"),
        "user": os.getenv("ADMIN_DB_USER", "admin"),
        "password": os.getenv("ADMIN_DB_PASS", "secret"),
        "host": detect_host(),
        "port": os.getenv("DB_PORT", "5432"),
    }
}


def get_connection(db_key="default"):
    """
    Returns a psycopg2 connection for the given db_key.
    - db_key="default" → packetdb / packetuser
    - db_key="admin_db" → packets / admin
    """
    import psycopg2
    config = DATABASES[db_key]
    return psycopg2.connect(**config)
