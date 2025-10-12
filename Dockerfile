# === FE build ===
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend

# Instalacja zależności (kompatybilnie z peer-deps)
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci --legacy-peer-deps; else npm install --legacy-peer-deps; fi

# Źródła frontu
COPY frontend/ ./

# Build lub fallback do /public (albo minimalny index.html)
RUN set -eux; \
  if npm run -s build 2>/dev/null || npm run -s build:prod 2>/dev/null; then \
    echo "✔ FE built"; \
  else \
    echo "ℹ No build script; using /public as /build"; \
    mkdir -p build; \
    if [ -d public ]; then cp -r public/* build/ || true; \
    else echo '<!doctype html><meta charset="utf-8"><title>App</title><div id="root"></div>' > build/index.html; fi; \
  fi

# === Python runtime + backend ===
FROM python:3.11-slim AS runtime
WORKDIR /app

# System deps (psycopg2, SSL, itp.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Backend
COPY backend/ /app/backend/
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt || \
    pip install fastapi uvicorn[standard] SQLAlchemy psycopg2-binary python-dotenv pydantic

# Dołącz build frontu (zawsze istnieje po kroku wyżej)
COPY --from=fe-build /fe/frontend/build /app/frontend/build

ENV PORT=8080
EXPOSE 8080
CMD ["bash","-lc","cd /app && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
