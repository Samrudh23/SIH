# ==============================================================================
# SIH26034 — Packaged Commodity Compliance Scanner
# Production Multi-Stage Containerfile
# ==============================================================================

# --- Stage 1: Build & Dependencies ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies in an isolated virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Production Runtime ---
FROM python:3.12-slim AS runtime

LABEL maintainer="SIH26034 Team"
LABEL description="SIH26034 Legal Metrology Packaged Commodities Compliance Scanner"
LABEL version="1.0.0"

# Install runtime dependencies (tesseract-ocr for P1 extraction fallback, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user and persistent data directories
RUN groupadd -r sihuser && useradd -r -g sihuser -u 1001 -m -s /bin/bash sihuser && \
    mkdir -p /app /data/uploads /data/db && \
    chown -R sihuser:sihuser /app /data

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=sihuser:sihuser /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend and frontend source trees
COPY --chown=sihuser:sihuser backend /app/backend
COPY --chown=sihuser:sihuser frontend /app/frontend

# Set production environment variables
ENV PYTHONPATH="/app/backend" \
    APP_ENV="production" \
    DEBUG="false" \
    HOST="0.0.0.0" \
    PORT="8000" \
    WEB_CONCURRENCY="2" \
    DATABASE_URL="sqlite:////data/db/sih26034.db" \
    UPLOAD_DIR="/data/uploads" \
    SERVE_FRONTEND="true" \
    FRONTEND_DIR="/app/frontend" \
    PYTHONUNBUFFERED="1"

# Switch to non-root user
USER sihuser

# Expose HTTP port
EXPOSE 8000

# Docker Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Launch production server via Uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
