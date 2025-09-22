FROM python:3.12-slim

WORKDIR /app

# Install dependencies (including gunicorn)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy app code
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Entrypoint runs init_db then starts Gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]

