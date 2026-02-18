# Etap 1: Budowanie frontendu w React (Node.js)
FROM node:20 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json frontend/yarn.lock* ./
RUN yarn install
COPY frontend/ ./
# KLUCZOWA ZMIANA: Fizycznie usuwamy fallback do localhosta z pliku busApi.js
RUN sed -i "s|const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';|const API_URL = '';|g" src/api/busApi.js
RUN yarn build

# Etap 2: Środowisko uruchomieniowe (Python + wbudowany frontend)
FROM python:3.11-slim
WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y gcc libxml2-dev libxslt-dev && rm -rf /var/lib/apt/lists/*

# Skopiowanie plików backendu
COPY backend/ /app/backend/

# Skopiowanie ZBUDOWANEGO frontendu z Etapu 1
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Instalacja zależności Python
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Uruchomienie aplikacji
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
