# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy only parser service requirements
COPY parser-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy parser service source explicitly
COPY parser-service/parser.py /app/parser.py

# Expose port (optional, but helps clarity)
EXPOSE 5001

# Use environment variable SERVICE_PORT for Gunicorn binding
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${SERVICE_PORT} parser:app"]

