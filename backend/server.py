import os
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

# Admin gate helpers
from admin_gate import require_admin, gate_page, login_api

ROOT = Path(__file__).parent
PUBLIC_DIR = ROOT / "public"
INDEX_FILE = PUBLIC_DIR / "index.html"

# --- App ---
app = FastAPI()

# CORS (open by default, możesz ograniczyć przez env CORS_ALLOW_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static /public (assets)
if PUBLIC_DIR.exists():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

# --- Optional Mongo (bez crasha, jeśli brak envów) ---
client = None
db = None
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")
if MONGO_URL and DB_NAME:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
    except Exception as e:
        logging.warning("Mongo init failed: %s", e)
else:
    logging.warning("Mongo disabled: MONGO_URL or DB_NAME not set")

# --- Admin routes ---
@app.get("/admin-gate", response_class=HTMLResponse)
async def admin_gate(request: Request):
    key = request.query_params.get("key")
    return gate_page(key)

@app.post("/api/admin/login")
async def admin_login(request: Request):
    return await login_api(request)

@app.get("/admin")
async def admin_panel(request: Request, _=Depends(require_admin)):
    admin_index = PUBLIC_DIR / "admin" / "index.html"
    if admin_index.exists():
        return FileResponse(str(admin_index))
    if INDEX_FILE.exists():
        return FileResponse(str(INDEX_FILE))
    return HTMLResponse("<h1>Admin OK</h1>")

# --- SPA fallback (serve index.html) ---
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if INDEX_FILE.exists():
        return FileResponse(str(INDEX_FILE))
    return HTMLResponse("<h1>OK</h1>")
