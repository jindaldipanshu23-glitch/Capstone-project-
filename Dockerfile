# Dockerfile for the Capstone FastAPI demo
FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Install system deps (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Upgrade pip and install python deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# Use PORT env var if provided by host (Render sets $PORT)
CMD ["sh", "-c", "uvicorn src.server.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
