FROM python:3.12-slim

WORKDIR /app

# Copy UI requirements
COPY ui-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy app code
COPY ui-service/app.py /app/app.py
COPY ui-service/templates /app/templates

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

