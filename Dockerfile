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

# ✅ NEW: install curl for health checks
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# ✅ NEW: create non-root user
RUN useradd -m -u 1000 appuser

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy project files
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# ✅ NEW: container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ✅ NEW: run as non-root
USER appuser

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "3", "--timeout", "90", "--graceful-timeout", "30", "--keep-alive", "5", "--bind", "0.0.0.0:8000"]