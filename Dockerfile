# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend

# Używamy NPM i nie zrywamy się na peer deps (CRA/webpack stare wersje)
ENV NPM_CONFIG_LEGACY_PEER_DEPS=true
ENV npm_config_legacy_peer_deps=true

# Skopiuj cały frontend
COPY frontend/ ./

# Wymuś NPM (ignoruj yarn.lock)
RUN rm -f yarn.lock \
 && if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Build (jeśli jest skrypt "build")
RUN if [ -f package.json ] && grep -q "\"build\"" package.json; then npm run build; else echo "Brak skryptu build – pomijam"; fi

# Znormalizuj artefakty do /fe/out
RUN mkdir -p /fe/out \
 && if [ -d build ]; then cp -r build/* /fe/out/; \
    elif [ -d dist ]; then cp -r dist/* /fe/out/; \
    elif [ -d public ]; then cp -r public/* /fe/out/; \
    else echo "Brak artefaktów frontendu – /fe/out puste"; fi

# ---------- Backend runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Kod backendu (opcjonalny) + zbudowany frontend
COPY backend/ /app/backend/
COPY --from=fe-build /fe/out /app/frontend/build

# Upewnij się, że backend to pakiet
RUN mkdir -p /app/backend \
 && [ -f /app/backend/__init__.py ] || printf "" > /app/backend/__init__.py

# Zależności Pythona
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastapi uvicorn starlette \
 && if [ -f /app/backend/requirements.txt ]; then pip install --no-cache-dir -r /app/backend/requirements.txt; fi

ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
