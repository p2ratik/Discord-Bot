FROM python:3.11-slim AS base

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

#Backend
FROM base AS backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Worker
FROM base AS worker
CMD ["python", "-m", "app.redis.worker"]