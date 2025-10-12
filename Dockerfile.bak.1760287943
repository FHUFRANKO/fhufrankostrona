# ===== FRONTEND BUILD =====
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci --legacy-peer-deps; else npm install --legacy-peer-deps; fi
COPY frontend/ ./
RUN npm run build || npm run build:prod || echo "no build script, skipping"

# ===== BACKEND RUNTIME =====
FROM python:3.11-slim AS runtime
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY backend/ /app/backend/
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt || \
    pip install fastapi uvicorn[standard] SQLAlchemy psycopg2-binary python-dotenv pydantic

# Dołącz build frontu (jeśli powstał)
COPY --from=fe-build /fe/frontend/build /app/frontend/build

ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8080"]
