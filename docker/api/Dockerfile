FROM python:3.12.3-slim

WORKDIR /app

# mysqlclient 빌드에 필요한 의존성(목적: WSL/로컬 차이 제거)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config \
    libmariadb-dev \
    ca-certificates \
    curl \
    && update-ca-certificates \
    && curl -fsSL https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /etc/ssl/certs/rds-global-bundle.pem \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# 운영환경을 위해 소스 코드 전체를 이미지 안에 넣기
COPY . /app/

CMD ["sh", "-lc", "set -eu; if [ -f /app/.env ]; then set -a; . /app/.env; set +a; fi; while true; do python manage.py publish_outbox_all_databases --databases=\"${OUTBOX_DATABASES:-posts_db,auth_db,events_db}\" --limit=\"${OUTBOX_PUBLISH_BATCH_SIZE:-50}\" --max-retries=\"${OUTBOX_MAX_RETRIES:-5}\" --retry-base-delay-seconds=\"${OUTBOX_RETRY_BASE_DELAY_SECONDS:-30}\"; sleep \"${OUTBOX_PUBLISH_INTERVAL_SECONDS:-3}\"; done"]
