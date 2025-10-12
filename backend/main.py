import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import router as ads_router

app = FastAPI()
app.include_router(ads_router)

# Serwuj zbudowany frontend (jeśli istnieje)
build_dir = (pathlib.Path(__file__).resolve().parent.parent / "frontend" / "build")
if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="static")
