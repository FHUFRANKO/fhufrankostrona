# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend

# Skopiuj cały frontend (najprościej i bez kruszenia się o locki)
COPY frontend/ ./

# Yarn albo npm – co znajdziemy
RUN corepack enable || true \
 && if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    else npm install; fi

# Build jeśli jest skrypt build
RUN if [ -f package.json ] && (cat package.json | grep -q "\"build\""); then \
       (yarn build || npm run build); \
    else \
       echo "Brak skryptu build – pomijam"; \
    fi

# Ujednolić ścieżkę wyjściową do /fe/out
RUN mkdir -p /fe/out \
 && if [ -d build ]; then cp -r build/* /fe/out/; \
    elif [ -d dist ]; then cp -r dist/* /fe/out/; \
    elif [ -d public ]; then cp -r public/* /fe/out/; \
    else echo "Brak artefaktów frontendu – /fe/out zostaje puste"; fi

# ---------- Backend runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Kod backendu (jeśli istnieje w repo)
COPY backend/ /app/backend/
# Zbudowany frontend trafia do /app/frontend/build
COPY --from=fe-build /fe/out /app/frontend/build

# Upewnij się, że backend jest pakietem
RUN mkdir -p /app/backend \
 && [ -f /app/backend/__init__.py ] || printf "" > /app/backend/__init__.py

# Zależności Pythona – minimum do FastAPI + opcjonalnie requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir fastapi uvicorn starlette \
 && if [ -f /app/backend/requirements.txt ]; then pip install --no-cache-dir -r /app/backend/requirements.txt; fi

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
