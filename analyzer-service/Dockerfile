# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copy service code explicitly
COPY analyzer-service/analyzer.py /app/analyzer.py
COPY analyzer-service/db_init.py /app/db_init.py

# Copy shared DB config from parent folder
COPY db_config.py /app/db_config.py

# First run db_init.py, then start Gunicorn
CMD ["sh", "-c", "python db_init.py && gunicorn -b 0.0.0.0:5003 analyzer:app"]

