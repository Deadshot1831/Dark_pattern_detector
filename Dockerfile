# Backend container for DeceptiTech.
#
# Uses the official Microsoft Playwright Python image, which ships with
# Chromium + every system library Playwright needs already installed.
# The image tag is pinned to match backend/requirements.txt's playwright
# version — they MUST match or Playwright won't find the browser.
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

# Python deps. Playwright is already in the base image, but we re-install
# from requirements.txt so the rest of the stack (fastapi, sqlalchemy, ...)
# is present and pinned.
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Application code + dataset (used by the LLM few-shot loader)
COPY backend /app/backend
COPY dark-patterns-v2.csv /app/dark-patterns-v2.csv

# Default storage paths (override in production by setting STORAGE_DIR /
# DATABASE_PATH to point at a mounted volume so scans + screenshots persist).
RUN mkdir -p /app/storage/screenshots /app/storage/llm_cache
ENV STORAGE_DIR=/app/storage \
    DATABASE_PATH=/app/storage/deceptitech.db \
    ALLOWED_ORIGINS=http://localhost:3000 \
    PORT=8000

EXPOSE 8000

# Shell form so $PORT is expanded at runtime (Railway / Render / Fly all
# inject $PORT and expect the app to bind to it).
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
