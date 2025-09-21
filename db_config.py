import os
import socket

def detect_host():
    """
    Detect whether we are running inside Docker Compose or on host.
    - If running inside Docker Compose, DB_HOST should be 'packets-db'
    - If running on EC2 host, DB_HOST should default to 'localhost'
    """
    # Priority: environment variable override
    db_host = os.getenv("DB_HOST")
    if db_host:
        return db_host

    # Try resolving 'packets-db' (works inside docker network)
    try:
        socket.gethostbyname("packets-db")
        return "packets-db"
    except socket.gaierror:
        return "localhost"

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "packetdb"),
    "user": os.getenv("DB_USER", "packetuser"),
    "password": os.getenv("DB_PASS", "packetpass"),
    "host": detect_host(),
    "port": os.getenv("DB_PORT", "5432")
}
