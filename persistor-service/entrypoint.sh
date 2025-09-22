#!/bin/sh
echo "Initializing DB schema..."
python -c "from persistor import init_db; init_db()"
echo "Starting Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:${SERVICE_PORT} persistor:app

