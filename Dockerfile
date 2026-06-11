FROM python:3.11-slim

WORKDIR /app

# Copy application code
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
 && pip install -r requirements.txt gunicorn

EXPOSE 5000

# Start the Flask app with gunicorn
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:5000", "app:app"]
