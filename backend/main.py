from pathlib import Path
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Jeśli masz własny backend/server.py:app – użyj go
try:
    from .server import app  # type: ignore
except Exception:
    app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range"],
)

# DB / modele / router
from .database import Base, engine, SessionLocal
from .routers import ads as ads_router
from .models import Ad

# Tworzenie tabel przy starcie
@app.on_event("startup")
def _on_startup():
    Base.metadata.create_all(bind=engine)

# Health
@app.get("/healthz", include_in_schema=False)
def healthz():
    return PlainTextResponse("ok")

# DEBUG: szybka diagnostyka DB i liczby rekordów
@app.get("/api/debug", include_in_schema=False)
def debug():
    try:
        db = SessionLocal()
        count = db.query(Ad).count()
        return {
            "db": (os.getenv("DATABASE_URL") or "sqlite").split("@")[-1][:120],
            "driver": str(engine.url.get_backend_name()),
            "count_ads": count,
            "env_port": os.getenv("PORT"),
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        try:
            db.close()
        except Exception:
            pass

# SEED: dodaj przykładowe ogłoszenie (wymaga ADMIN_TOKEN)
from .deps import admin_required, get_db
from .schemas import AdCreate
from sqlalchemy.orm import Session

@app.post("/api/seed", include_in_schema=False, dependencies=[Depends(admin_required)])
def seed(db: Session = Depends(get_db)):
    if db.query(Ad).count() == 0:
        demo = Ad(title="Demo ogłoszenie", description="To jest rekord testowy", price=34567, city="Szczecin",
                  image_url="https://images.unsplash.com/photo-1593941707874-ef25b8b4a92f?q=80&w=1200&auto=format&fit=crop")
        db.add(demo); db.commit()
    return {"ok": True, "count": db.query(Ad).count()}

# REST dla ogłoszeń
app.include_router(ads_router.router)

# Serwowanie SPA (pamiętaj: /api/* ma pierwszeństwo)
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
    def spa(full_path: str, request: Request):
        # Nigdy nie przechwytuj ścieżek API
        if request.url.path.startswith("/api"):
            raise HTTPException(404)
        return FileResponse(FRONTEND_BUILD / "index.html")
