# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend
# Zezwól npm na legacy peer deps (eliminujemy ERESOLVE)
ENV NPM_CONFIG_LEGACY_PEER_DEPS=true
ENV npm_config_legacy_peer_deps=true

# Skopiuj cały frontend
COPY frontend/ ./

# Install: yarn jeśli jest yarn.lock, w przeciwnym razie npm z legacy peer deps
RUN corepack enable || true \
 && if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci --legacy-peer-deps; \
    else npm install --legacy-peer-deps; fi

# Build (jeśli jest skrypt "build")
RUN if [ -f package.json ] && grep -q "\"build\"" package.json; then \
       (yarn build || npm run build); \
    else echo "Brak skryptu build – pomijam"; \
    fi

# Normalizacja artefaktów do /fe/out
RUN mkdir -p /fe/out \
 && if [ -d build ]; then cp -r build/* /fe/out/; \
    elif [ -d dist ]; then cp -r dist/* /fe/out/; \
    elif [ -d public ]; then cp -r public/* /fe/out/; \
    else echo "Brak artefaktów frontendu – /fe/out puste"; fi

# ---------- Backend runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Kod backendu (opcjonalnie) + zbudowany frontend
COPY backend/ /app/backend/
COPY --from=fe-build /fe/out /app/frontend/build

# Upewnij się, że backend to pakiet
RUN mkdir -p /app/backend \
 && [ -f /app/backend/__init__.py ] || printf "" > /app/backend/__init__.py

# Zależności Pythona (FastAPI + ewentualne requirements)
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastapi uvicorn starlette \
 && if [ -f /app/backend/requirements.txt ]; then pip install --no-cache-dir -r /app/backend/requirements.txt; fi

# Start serwera
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
