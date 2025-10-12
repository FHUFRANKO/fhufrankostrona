# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend
ENV NPM_CONFIG_LEGACY_PEER_DEPS=true npm_config_legacy_peer_deps=true
COPY frontend/ ./
RUN rm -f yarn.lock && if [ -f package-lock.json ]; then npm ci; else npm install; fi
RUN if [ -f package.json ] && grep -q "\"build\"" package.json; then npm run build; else echo "no build script"; fi
RUN mkdir -p /fe/out && \
    if [ -d build ]; then cp -r build/* /fe/out/; \
    elif [ -d dist ]; then cp -r dist/* /fe/out/; \
    elif [ -d public ]; then cp -r public/* /fe/out/; fi

# ---------- Backend runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000

# Najpierw zainstaluj zależności backendu
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Potem dopiero kod aplikacji + zbudowany frontend
COPY backend/ /app/backend/
COPY --from=fe-build /fe/out /app/frontend/build

# Upewnij się, że backend to pakiet Pythona
RUN mkdir -p /app/backend && [ -f /app/backend/__init__.py ] || printf "" > /app/backend/__init__.py

EXPOSE 8000
CMD ["sh","-c","uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
