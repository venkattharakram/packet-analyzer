# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

# First run db_init.py, then start Gunicorn
CMD ["sh", "-c", "python db_init.py && gunicorn -b 0.0.0.0:5003 analyzer:app"]

