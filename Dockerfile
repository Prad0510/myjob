# syntax=docker/dockerfile:1
FROM python:3.11-slim as base

# Prevent Python from writing .pyc files and keep stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

WORKDIR /app

# Install system dependencies required for compiling extensions & PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache the sentence transformer embedding model to avoid runtime download delay
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy source code and config
COPY . .

# Create logs directory and non-root user
RUN mkdir -p logs data/raw data/processed && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Default command starts the scheduler daemon
CMD ["python", "-m", "src.jobs.scheduler"]

