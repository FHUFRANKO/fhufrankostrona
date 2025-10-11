from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

# Jeśli masz własne API w backend/server.py z obiektem `app`, to go użyj:
try:
    from .server import app  # type: ignore
except Exception:
    app = FastAPI()

# Prosty healthcheck dla Railway
@app.get("/healthz", include_in_schema=False)
def healthz():
    return PlainTextResponse("ok")

# Serwowanie zbudowanego frontendu (SPA)
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_BUILD = BASE_DIR / "frontend" / "build"

if FRONTEND_BUILD.exists():
    static_dir = FRONTEND_BUILD / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(FRONTEND_BUILD / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        index = FRONTEND_BUILD / "index.html"
        return FileResponse(index if index.exists() else FRONTEND_BUILD / "index.html")
