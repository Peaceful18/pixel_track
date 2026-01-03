FROM python:3.12 AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app

COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN chown -R appuser:appgroup /app /opt/venv

USER appuser

EXPOSE 8000
CMD ["uvicorn", "ingest_api.main:app", "--host", "0.0.0.0", "--port", "8000"]