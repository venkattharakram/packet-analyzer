# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Use environment variable SERVICE_PORT for Gunicorn binding
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${SERVICE_PORT} parser:app"]

