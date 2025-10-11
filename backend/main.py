from pathlib import Path

# 1) Użyj istniejącej aplikacji FastAPI z backend/server.py, jeśli jest dostępna
try:
    from .server import app  # type: ignore
except Exception:
    from fastapi import FastAPI
    app = FastAPI()

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_BUILD = BASE_DIR / "frontend" / "build"

# 2) Serwuj statyczny frontend (CRA build)
if FRONTEND_BUILD.exists():
    static_dir = FRONTEND_BUILD / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(FRONTEND_BUILD / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        # SPA fallback dla tras klienckich (React Router itp.)
        return FileResponse(FRONTEND_BUILD / "index.html")
