from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.responses import FileResponse
from admin_gate import require_admin, gate_page, login_api
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.getenv('MONGO_URL')



db_name = os.getenv('DB_NAME')

# --- Optional MongoDB init (skipped when MONGO_URL or DB_NAME is missing) ---
client = None
db = None
if mongo_url and db_name:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(mongo_url)
        try:
            db = (client[db_name] if (client is not None and db_name) else None)
        except Exception:
            db = None
    except Exception:
        client = None
        db = None
else:
    import logging
    logging.warning("Mongo disabled: MONGO_URL or DB_NAME not set")
# --- end optional MongoDB init ---
# --- optional MongoDB init (skipped when MONGO_URL is not set) ---
client = None
db = None
if mongo_url:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(mongo_url)
        try:
            db = client.get_default_database()
        except Exception:
            pass
    except Exception:
        # If motor is not installed or URL invalid, skip silently
        pass
else:
    import logging
    logging.warning("MONGO_URL not set; skipping MongoDB init")
# --- end optional MongoDB init ---
client = AsyncIOMotorClient(mongo_url)
db = (client[db_name] if (client is not None and db_name) else None)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# --- Static frontend (SPA) serwowany przez FastAPI ---
from pathlib import Path
from fastapi.staticfiles import StaticFiles

_PUBLIC_DIR = Path(__file__).parent / "public"
if _PUBLIC_DIR.exists():
    # Uwaga: API-routry powinny być zarejestrowane powyżej.
    # html=True → index.html jako fallback dla tras SPA.
    app.mount("/", StaticFiles(directory=str(_PUBLIC_DIR), html=True), name="frontend")


@app.get("/admin-gate")
async def admin_gate(request: Request):
    key = request.query_params.get("key")
    return gate_page(key)

@app.post("/api/admin/login")
async def admin_login(payload: dict):
    return await login_api(payload)

# przykład ochrony: wejście do panelu
@app.get("/admin")
async def admin_root(_=Depends(require_admin)):
    # jeśli panel to SPA z public/index.html – dostosuj ścieżkę:
    try:
        return FileResponse("public/index.html")
    except Exception:
        # fallback — jeśli admin ma osobny index
        return FileResponse("public/admin/index.html")
