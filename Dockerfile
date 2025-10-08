# --- Build frontendu (React/CRACO) ---
FROM node:20-alpine AS fe
WORKDIR /app/frontend
COPY frontend/package.json ./
# skopiuj locka jeśli istnieje (nie przerywaj, jeśli go nie ma)
COPY frontend/yarn.lock ./ 2>/dev/null || true
RUN corepack enable
# install: preferuj yarn, fallback na npm
RUN if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    else npm ci || npm install; fi
COPY frontend ./
RUN if [ -f package.json ]; then \
      if [ -f yarn.lock ]; then yarn build; else npm run build; fi; \
    fi

# --- Runtime backendu (Python 3.11) ---
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# skopiuj cały backend i zainstaluj zależności jeśli istnieją
COPY backend ./backend
RUN if [ -f backend/requirements.txt ]; then \
      pip install --no-cache-dir -r backend/requirements.txt; \
    fi

# wgraj build frontu do backend/public (jeśli zbudowano)
RUN mkdir -p ./backend/public
COPY --from=fe /app/frontend/build ./backend/public

WORKDIR /app/backend
EXPOSE 8000
ENV PORT=8000
# uruchom FastAPI / Uvicorn – nie zmienia kodu
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
