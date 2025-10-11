# syntax=docker/dockerfile:1

# ---------- Frontend build ----------
FROM node:20-alpine AS fe-build
WORKDIR /fe/frontend
# Manifests (cache)
COPY frontend/package.json ./package.json
COPY frontend/yarn.lock ./yarn.lock
COPY frontend/package-lock.json ./package-lock.json
# Yarn/NPM install
RUN corepack enable || true
RUN (yarn install --frozen-lockfile || npm ci || npm install)
# Źródła + build
COPY frontend/ ./
RUN (yarn build || npm run build)

# ---------- Backend runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Kod backendu + zbudowany frontend
COPY backend/ /app/backend/
COPY --from=fe-build /fe/frontend/build /app/frontend/build

# Upewnij się, że backend jest pakietem Pythona
RUN [ -f backend/__init__.py ] || printf "" > backend/__init__.py

# Zależności Pythona
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt

# Start FastAPI (port podany przez Railway)
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
