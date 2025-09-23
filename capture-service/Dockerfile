FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY capture-service/capture.py .

ENTRYPOINT ["python3", "capture.py"]

