# Multi-stage Dockerfile for PERSONA-X Universal Intelligence Platform

# --- Stage 1: Build Frontend Assets ---
FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Backend & Fullstack Runner ---
FROM python:3.11-slim AS production

# System dependencies for cryptography, curl, and network inspection
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
# Install core runtime dependencies in case requirements.txt is absent
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    sqlalchemy \
    alembic \
    psycopg2-binary \
    pydantic \
    pydantic-settings \
    httpx \
    python-dotenv \
    sentry-sdk \
    argon2-cffi \
    pyjwt \
    beautifulsoup4 \
    lxml

# Copy backend source and engine
COPY backend/ ./backend/
COPY engine/ ./engine/
COPY alembic.ini ./alembic.ini
COPY data/ ./data/

# Copy built frontend assets into frontend/dist for static & SPA serving
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

# Ensure data and logs directories exist with proper write permissions
RUN mkdir -p /app/data /app/logs

# Default environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
