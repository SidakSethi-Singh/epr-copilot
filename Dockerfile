FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 AS lambda-adapter

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    AWS_LWA_PORT=5000 \
    FLASK_DEBUG=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=lambda-adapter /lambda-adapter /opt/extensions/lambda-adapter

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--workers=1", "--bind=0.0.0.0:5000", "--timeout=60", "--access-logfile=-", "app:app"]
