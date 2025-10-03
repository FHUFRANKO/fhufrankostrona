#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/backend"

python3 -m pip install --upgrade pip setuptools wheel
if [ -f requirements.txt ]; then
  python3 -m pip install -r requirements.txt
fi

# Jeśli Twój entrypoint to inny plik niż server.py, zmień poniższą linię.
exec uvicorn server:app --host 0.0.0.0 --port "${PORT:-8000}"
