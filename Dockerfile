# Use a small official Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (if any) and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port used by config.py (default 8051)
ENV PORT=8051
EXPOSE 8051

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Use Gunicorn to serve the Flask app exposed by Dash
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8051", "app_v2:server"]
