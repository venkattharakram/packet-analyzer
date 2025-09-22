FROM python:3.12-slim

WORKDIR /app

# Install dependencies (including gunicorn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy service code explicitly
COPY persistor-service/persistor.py /app/persistor.py
# Copy shared DB config from parent folder
COPY ../db_config.py /app/db_config.py

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Entrypoint runs init_db then starts Gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]

