from pathlib import Path
import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range"],
)

from .database import Base, engine, SessionLocal
from .routers import ads as ads_router
from .models import Ad
from .deps import admin_required, get_db

@app.on_event("startup")
def _on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB init skipped:", e)

@app.get("/healthz", include_in_schema=False)
def healthz():
    return PlainTextResponse("ok")

@app.get("/api/debug", include_in_schema=False)
def debug():
    try:
        from sqlalchemy import text
        db = SessionLocal()
        count = db.execute(text("select count(*) from ads")).scalar_one_or_none()
        return {"driver": str(engine.url.get_backend_name()),
                "database": str(engine.url).split("@")[-1],
                "count_ads": int(count or 0),
                "env_port": os.getenv("PORT")}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        try: db.close()
        except Exception: pass

@app.post("/api/seed", include_in_schema=False, dependencies=[Depends(admin_required)])
def seed(db: Session = Depends(get_db)):
    if db.query(Ad).count() == 0:
        demo = Ad(title="Demo ogłoszenie", description="Rekord testowy", price=12345, city="Szczecin",
                  image_url="https://images.unsplash.com/photo-1593941707874-ef25b8b4a92f?q=80&w=1200&auto=format&fit=crop")
        db.add(demo); db.commit()
    return {"ok": True, "count": db.query(Ad).count()}

# API
app.include_router(ads_router.router)

# Frontend – serwuj /static (CRA) i /assets (Vite) oraz fallback na index.html
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_BUILD = BASE_DIR / "frontend" / "build"

if FRONTEND_BUILD.exists():
    # Montuj oba katalogi jeśli istnieją
    s = FRONTEND_BUILD / "static"
    a = FRONTEND_BUILD / "assets"
    if s.exists():
        app.mount("/static", StaticFiles(directory=s), name="static")
    if a.exists():
        app.mount("/assets", StaticFiles(directory=a), name="assets")

    INDEX = FRONTEND_BUILD / "index.html"

    @app.get("/", include_in_schema=False)
    def index():
        # no-cache dla index.html, żeby przeglądarka nie trzymała starego
        headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
        return FileResponse(INDEX, headers=headers)

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str, request: Request):
        if request.url.path.startswith("/api"):
            raise HTTPException(404)
        headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
        return FileResponse(INDEX, headers=headers)
