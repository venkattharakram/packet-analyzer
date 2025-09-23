FROM python:3.12-slim

WORKDIR /app

# Copy requirements specific to this service
COPY capture-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code explicitly
COPY capture-service/capture.py /app/capture.py

ENTRYPOINT ["python3", "capture.py"]
