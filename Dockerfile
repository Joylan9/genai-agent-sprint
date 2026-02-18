# ============================
# Stage 1 — Builder
# ============================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt


# ============================
# Stage 2 — Runtime
# ============================
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Copy project files
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "3", "--timeout", "90", "--graceful-timeout", "30", "--keep-alive", "5", "--bind", "0.0.0.0:8000"]
