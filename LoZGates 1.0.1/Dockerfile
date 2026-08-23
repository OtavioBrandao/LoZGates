FROM python:3.12-slim

WORKDIR /app

COPY requirements-service.txt ./
RUN pip install --no-cache-dir -r requirements-service.txt

COPY config.py ./
COPY BackEnd ./BackEnd
COPY services ./services

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOZGATES_DATA_DIR=/app/data \
    LOZGATES_LOG_DIR=/app/logs

RUN useradd --create-home --uid 10001 lozgates \
    && mkdir -p /app/data /app/logs \
    && chown -R lozgates:lozgates /app

USER lozgates
EXPOSE 8000

CMD ["python", "-m", "services.ai_service"]
