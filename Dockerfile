# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend
ENV NPM_CONFIG_LEGACY_PEER_DEPS=true
ENV npm_config_legacy_peer_deps=true

COPY frontend/ ./
RUN rm -f yarn.lock \
 && if [ -f package-lock.json ]; then npm ci; else npm install; fi

RUN if [ -f package.json ] && grep -q "\"build\"" package.json; then npm run build; else echo "Brak skryptu build – pomijam"; fi

RUN mkdir -p /fe/out \
 && if [ -d build ]; then cp -r build/* /fe/out/; \
    elif [ -d dist ]; then cp -r dist/* /fe/out/; \
    elif [ -d public ]; then cp -r public/* /fe/out/; \
    else echo "Brak artefaktów frontendu – /fe/out puste"; fi

# ---------- Backend runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY backend/ /app/backend/
COPY --from=fe-build /fe/out /app/frontend/build

RUN mkdir -p /app/backend \
 && [ -f /app/backend/__init__.py ] || printf "" > /app/backend/__init__.py

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastapi uvicorn starlette \
 && if [ -f /app/backend/requirements.txt ]; then pip install --no-cache-dir -r /app/backend/requirements.txt; fi

# Użyj portu z ENV PORT (Railway go ustawia)
ENV PORT=8000
EXPOSE 8000
CMD ["sh","-c","uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
