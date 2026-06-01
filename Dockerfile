FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables (overridable at runtime)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

# Run with gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
