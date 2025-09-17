FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY persistor.py /app/

EXPOSE 5002
CMD ["python", "persistor.py"]
