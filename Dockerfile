# Multi-stage Dockerfile for Enterprise SaaS Backend Foundation

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set environment variables for pip
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements files
COPY requirements ./requirements

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip wheel --wheel-dir=/wheels -r requirements/docker.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH \
    DJANGO_SETTINGS_MODULE=foundation.config.settings.docker

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy wheels from builder and install
COPY --from=builder /wheels /wheels
COPY requirements ./requirements
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-index --find-links=/wheels -r requirements/docker.txt && \
    rm -rf /wheels

# Create non-root user
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "foundation/manage.py", "runserver", "0.0.0.0:8000"]
