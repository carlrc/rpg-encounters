# Multi-stage Dockerfile for RPG Encounters Backend

# Stage 1: Base Python image with system dependencies
FROM python:3.11.13-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    postgresql-client \
    gcc \
    g++ \
    make \
    curl \
    debian-keyring \
    debian-archive-keyring \
    apt-transport-https \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install -y caddy \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: Install Python dependencies
FROM base AS dependencies

# Install uv package manager
RUN pip install uv

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv venv .venv
RUN uv sync

# Stage 3: Runtime image
FROM base AS runtime

# Create non-root user
RUN useradd --create-home --shell /bin/bash --user-group app

# Copy virtual environment from dependencies stage
COPY --from=dependencies --chown=app:app /app/.venv /app/.venv

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=app:app app/ ./app/

# Copy Caddy configuration and entrypoint script
COPY --chown=app:app Caddyfile ./Caddyfile
COPY --chown=app:app entrypoint.sh ./entrypoint.sh

# Make entrypoint script executable
USER root
RUN chmod +x ./entrypoint.sh
USER app

# Switch to non-root user
USER app

# Expose ports (8000 for development, 443 for production HTTPS)
EXPOSE 8000 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application via entrypoint script
ENTRYPOINT ["./entrypoint.sh"]