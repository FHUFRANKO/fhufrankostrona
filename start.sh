#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# --- ZAINSTALUJ BACKEND ---
cd "$REPO_ROOT/backend"
python3 -m pip install --upgrade pip setuptools wheel
if [ -f requirements.txt ]; then
  python3 -m pip install -r requirements.txt
fi

# --- ZBUDUJ FRONTEND (jesli istnieje) ---
if [ -d "$REPO_ROOT/frontend" ]; then
  cd "$REPO_ROOT/frontend"
  # Włącz corepack → Yarn będzie dostępny
  if command -v corepack >/dev/null 2>&1; then corepack enable || true; fi
  # Instalacja zależności
  if [ -f yarn.lock ]; then
    yarn install --frozen-lockfile || yarn install
    yarn build
  else
    npm ci || npm install
    npm run build
  fi
  # Kopia buildu do backend/public
  mkdir -p "$REPO_ROOT/backend/public"
  rm -rf "$REPO_ROOT/backend/public/"*
  cp -R "$REPO_ROOT/frontend/build/"* "$REPO_ROOT/backend/public/"
fi

# --- START FASTAPI ---
cd "$REPO_ROOT/backend"
exec uvicorn server:app --host 0.0.0.0 --port "${PORT:-8000}"
