# --- Build frontendu (React/CRACO) ---
FROM node:20-alpine AS fe
WORKDIR /app/frontend
# kopiujemy cały frontend (to proste i pewne)
COPY frontend/ ./
RUN corepack enable \
 && if [ -f yarn.lock ]; then yarn install --frozen-lockfile; else npm ci || npm install; fi \
 && if [ -f package.json ]; then \
      if [ -f yarn.lock ]; then yarn build; else npm run build; fi; \
    fi

# --- Runtime backendu (Python 3.11) ---
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# kod backendu i zależności (jeśli plik istnieje)
COPY backend ./backend
RUN if [ -f backend/requirements.txt ]; then \
      pip install --no-cache-dir -r backend/requirements.txt; \
    fi

# statyczny build frontu trafia do backend/public
RUN mkdir -p ./backend/public
COPY --from=fe /app/frontend/build ./backend/public

WORKDIR /app/backend
EXPOSE 8000
ENV PORT=8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
