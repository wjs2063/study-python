FROM python:3.13-slim
LABEL authors="jeonjaehyeon"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1 \
    PYTHONPATH=/app/src \
    APP_MODULE="main:app" \
    HOST="0.0.0.0" \
    PORT="8000" \
    LOG_LEVEL="info" \
    TZ="Asia/Seoul"

WORKDIR /app

# 1) 루트 컨텍스트에서 종속성 파일만 먼저 복사(레이어 캐시)
COPY pyproject.toml uv.lock ./

# 2) uv 전역 설치 (lock 고정, dev 제외)
RUN uv sync --frozen --no-dev

# 3) 앱 소스 복사 (루트 컨텍스트 기준 경로)
ARG SRC_DIR=backend/eft/application/src
COPY ${SRC_DIR} ./src

EXPOSE 8000
CMD uv run uvicorn ${APP_MODULE} --host ${HOST} --port ${PORT} --log-level ${LOG_LEVEL} --no-access-log
