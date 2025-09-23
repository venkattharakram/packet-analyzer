# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy service code explicitly
COPY persistor-service/persistor.py /app/persistor.py
# Copy shared DB config from parent folder
COPY db_config.py /app/db_config.py

# Use environment variable SERVICE_PORT for Gunicorn binding
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${SERVICE_PORT} persistor:app"]
