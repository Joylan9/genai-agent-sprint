# ============================
# Stage 1 — Builder
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

# lighter dev toolset (avoid huge build-essential during heavy builds)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
# prefer binary wheels, avoid pip cache, install into /install for multi-stage copy
RUN pip install --no-cache-dir --prefer-binary --prefix=/install -r requirements.txt


# ============================
# Stage 2 — Runtime
# ============================
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy project files
COPY . .

# Keep Python behavior predictable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set application-owned cache locations (transformers/hf use these)
# We set HOME and multiple cache envs so HF/transformers/sentence-transformers will use /app/.cache
ENV HOME=/app \
    XDG_CACHE_HOME=/app/.cache \
    HF_HOME=/app/.cache \
    TRANSFORMERS_CACHE=/app/.cache \
    HF_DATASETS_CACHE=/app/.cache

# Create cache dirs and a non-root user, ensure ownership (must run as root)
RUN mkdir -p /app/.cache/huggingface /app/.cache/hub \
    && groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user (enterprise practice)
USER appuser

EXPOSE 8000

# NOTE: use the correct module path for your FastAPI app (api.app:app)
CMD ["gunicorn", "api.app:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "3", "--timeout", "90", "--graceful-timeout", "30", "--keep-alive", "5", "--bind", "0.0.0.0:8000"]