#!/usr/bin/env bash
set -euo pipefail

# wejdź do backend/
cd "$(dirname "$0")/backend"

# zaktualizuj pip i zainstaluj zależności (jeśli plik istnieje)
python -m pip install --upgrade pip setuptools wheel
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# uruchom FastAPI (zakładamy backend/server.py z obiektem "app")
exec uvicorn server:app --host 0.0.0.0 --port "${PORT:-8000}"
