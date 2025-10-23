from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
from datetime import datetime, date
import os
import hmac
import hashlib
import logging
import uuid
import jwt
import requests
from bs4 import BeautifulSoup
import re
from supabase import create_client, Client

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create uploads directory
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Admin Panel Configuration
ADMIN_PATH = os.getenv("ADMIN_PATH", "moj-tajny-panel-82374")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ZmienMnieTeraz123!")
ADMIN_COOKIE_SECRET = os.getenv("ADMIN_COOKIE_SECRET", "ZmienTenSekret123!")
ADMIN_COOKIE_NAME = "admin_session"

def _sign(value: str) -> str:
    """Sign a value with HMAC-SHA256"""
    return hmac.new(ADMIN_COOKIE_SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()

# Supabase client (database + storage)
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_bucket = os.environ.get('SUPABASE_BUCKET', 'bus-images')

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

supabase: Client = create_client(supabase_url, supabase_key)

# --- AUTH START ---
oauth2_scheme = HTTPBearer(auto_error=False)
JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET', '')
ADMIN_EMAILS = set(e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip())

def verify_supabase_token(token: str) -> dict:
    """Verify Supabase JWT token"""
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET not configured")
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"], 
            options={"verify_aud": False}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """Get current authenticated user from JWT token"""
    if not creds:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="SUPABASE_JWT_SECRET not configured")
    
    payload = verify_supabase_token(creds.credentials)
    return payload

async def get_current_user_optional(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """Get current user from JWT or cookie session"""
    # Try cookie first (password-based admin access)
    cookie_token = request.cookies.get(ADMIN_COOKIE_NAME)
    if cookie_token == _sign("ok"):
        return {"email": "admin@cookie", "auth_method": "cookie"}
    
    # Try JWT token
    if creds and JWT_SECRET:
        try:
            payload = verify_supabase_token(creds.credentials)
            return {**payload, "auth_method": "jwt"}
        except:
            pass
    
    raise HTTPException(status_code=401, detail="Authentication required")

def admin_required(user: dict = Depends(get_current_user_optional)):
    """Dependency to require admin privileges (cookie or JWT)"""
    # Cookie-based access is always admin
    if user.get("auth_method") == "cookie":
        return user
    
    # JWT-based access requires email in whitelist
    if user.get("auth_method") == "jwt":
        email = (user.get('email') or '').lower()
        if email not in ADMIN_EMAILS:
            raise HTTPException(
                status_code=403, 
                detail=f"Admin access required. Email '{email}' is not in admin list."
            )
        return user
    
    raise HTTPException(status_code=403, detail="Admin access required")
# --- AUTH END ---

# Create the main app without a prefix
app = FastAPI()

# Admin Panel Guard Middleware
@app.middleware("http")
async def _admin_guard(request: Request, call_next):
    """Protect all /admin* routes with cookie-based authentication"""
    path = request.url.path
    
    # Check if accessing admin area (but not the login gate itself)
    if path.startswith("/admin") and not path.startswith(f"/admin-{ADMIN_PATH}"):
        token = request.cookies.get(ADMIN_COOKIE_NAME)
        
        # If no valid session, redirect to hidden login page
        if token != _sign("ok"):
            return RedirectResponse(url=f"/admin-{ADMIN_PATH}", status_code=303)
    
    response = await call_next(request)
    return response

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Auth endpoint
@api_router.get("/me")
async def get_me(user: dict = Depends(get_current_user_optional)):
    """Get current user info and admin status"""
    if user.get("auth_method") == "cookie":
        return {
            "email": "admin (cookie-based)",
            "admin": True,
            "auth_method": "cookie",
            "authenticated": True
        }
    
    email = (user.get('email') or '').lower()
    return {
        "email": email,
        "admin": email in ADMIN_EMAILS if ADMIN_EMAILS else False,
        "user_id": user.get('sub'),
        "auth_method": "jwt",
        "authenticated": True
    }

# --- MODELS ---
class Bus(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    marka: str
    model: str
    rok: int
    przebieg: int
    paliwo: str
    skrzynia: str
    naped: Optional[str] = None
    cenaBrutto: int
    cenaNetto: Optional[int] = None
    vat: bool = True
    typNadwozia: str
    moc: int
    kubatura: Optional[int] = None
    normaSpalania: Optional[str] = None
    normaEmisji: str
    dmcKategoria: str
    ladownosc: int
    wymiarL: Optional[str] = None
    wymiarH: Optional[str] = None
    liczbaMiejsc: Optional[int] = None
    liczbaPalet: Optional[int] = None
    klima: bool = False
    tempomat: bool = False
    kamera: bool = False
    czujnikiParkowania: bool = False
    hak: bool = False
    asystentPasa: bool = False
    bluetooth: bool = False
    opis: Optional[str] = None
    wyposazenie: List[str] = []
    zdjecia: List[str] = []
    zdjecieGlowne: Optional[str] = None
    wyrozniowane: bool = False
    nowosc: bool = False
    flotowy: bool = False
    gwarancja: bool = False
    numerOgloszenia: Optional[str] = None
    dataPublikacji: str = Field(default_factory=lambda: datetime.now().isoformat())

class BusCreate(BaseModel):
    marka: str
    model: str
    rok: int
    przebieg: int
    paliwo: str
    skrzynia: str
    naped: Optional[str] = None
    cenaBrutto: int
    cenaNetto: Optional[int] = None
    vat: bool = True
    typNadwozia: str
    moc: int
    kubatura: Optional[int] = None
    normaSpalania: Optional[str] = None
    normaEmisji: str
    dmcKategoria: str
    ladownosc: int
    wymiarL: Optional[str] = None
    wymiarH: Optional[str] = None
    liczbaMiejsc: Optional[int] = None
    liczbaPalet: Optional[int] = None
    klima: bool = False
    tempomat: bool = False
    kamera: bool = False
    czujnikiParkowania: bool = False
    hak: bool = False
    asystentPasa: bool = False
    bluetooth: bool = False
    opis: Optional[str] = None
    wyposazenie: List[str] = []
    zdjecia: List[str] = []
    zdjecieGlowne: Optional[str] = None
    wyrozniowane: bool = False
    nowosc: bool = False
    flotowy: bool = False
    gwarancja: bool = False
    numerOgloszenia: Optional[str] = None

class BusUpdate(BaseModel):
    marka: Optional[str] = None
    model: Optional[str] = None
    rok: Optional[int] = None
    przebieg: Optional[int] = None
    paliwo: Optional[str] = None
    skrzynia: Optional[str] = None
    naped: Optional[str] = None
    cenaBrutto: Optional[int] = None
    cenaNetto: Optional[int] = None
    vat: Optional[bool] = None
    typNadwozia: Optional[str] = None
    moc: Optional[int] = None
    kubatura: Optional[int] = None
    normaSpalania: Optional[str] = None
    normaEmisji: Optional[str] = None
    dmcKategoria: Optional[str] = None
    ladownosc: Optional[int] = None
    wymiarL: Optional[str] = None
    wymiarH: Optional[str] = None
    liczbaMiejsc: Optional[int] = None
    liczbaPalet: Optional[int] = None
    klima: Optional[bool] = None
    tempomat: Optional[bool] = None
    kamera: Optional[bool] = None
    czujnikiParkowania: Optional[bool] = None
    hak: Optional[bool] = None
    asystentPasa: Optional[bool] = None
    bluetooth: Optional[bool] = None
    opis: Optional[str] = None
    wyposazenie: Optional[List[str]] = None
    zdjecia: Optional[List[str]] = None
    zdjecieGlowne: Optional[str] = None
    wyrozniowane: Optional[bool] = None
    nowosc: Optional[bool] = None
    flotowy: Optional[bool] = None
    gwarancja: Optional[bool] = None

class Opinion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    imie: str
    nazwisko: str
    rodzajFirmy: str
    opinia: str
    zakupionyPojazd: str
    ocena: int = 5
    wyswietlaj: bool = True
    dataPublikacji: str = Field(default_factory=lambda: datetime.now().isoformat())

class OpinionCreate(BaseModel):
    imie: str
    nazwisko: str
    rodzajFirmy: str
    opinia: str
    zakupionyPojazd: str
    ocena: int = 5
    wyswietlaj: bool = True

class OpinionUpdate(BaseModel):
    imie: Optional[str] = None
    nazwisko: Optional[str] = None
    rodzajFirmy: Optional[str] = None
    opinia: Optional[str] = None
    zakupionyPojazd: Optional[str] = None
    ocena: Optional[int] = None
    wyswietlaj: Optional[bool] = None

class AdminLoginRequest(BaseModel):
    password: str

# --- API ENDPOINTS ---

@api_router.get("/")
async def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "FHU FRANKO API"}

# Upload image endpoint
@api_router.post("/upload", response_model=dict, dependencies=[Depends(admin_required)])
async def upload_image(file: UploadFile = File(...)):
    """Upload image to Supabase Storage or local fallback"""
    try:
        # Read file content
        contents = await file.read()
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Try Supabase first
        try:
            file_path = f"buses/{unique_filename}"
            result = supabase.storage.from_(supabase_bucket).upload(
                file_path,
                contents,
                file_options={"content-type": file.content_type}
            )
            
            # Get public URL
            public_url = supabase.storage.from_(supabase_bucket).get_public_url(file_path)
            
            return {
                "success": True,
                "url": public_url,
                "filename": unique_filename,
                "storage": "supabase"
            }
        except Exception as supabase_error:
            logger.warning(f"Supabase upload failed, using local storage: {str(supabase_error)}")
            
            # Fallback to local storage
            upload_dir = ROOT_DIR / "uploads" / "buses"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / unique_filename
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Return relative URL
            public_url = f"/uploads/buses/{unique_filename}"
            
            return {
                "success": True,
                "url": public_url,
                "filename": unique_filename,
                "storage": "local"
            }
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Bus CRUD endpoints
@api_router.post("/ogloszenia", response_model=Bus, dependencies=[Depends(admin_required)])
async def create_bus(bus_data: BusCreate):
    """Create a new bus listing"""
    bus_dict = bus_data.dict()
    bus_id = str(uuid.uuid4())
    bus_dict['id'] = bus_id
    bus_dict['dataPublikacji'] = datetime.now().isoformat()
    
    # Generate unique listing number if not provided
    if not bus_dict.get('numerOgloszenia'):
        # Count existing buses
        response = supabase.table('buses').select('id', count='exact').execute()
        count = response.count if hasattr(response, 'count') else len(response.data)
        bus_dict['numerOgloszenia'] = f"FKBUS{str(count + 1).zfill(6)}"
    
    # Insert into Supabase
    response = supabase.table('buses').insert(bus_dict).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create bus")
    
    return Bus(**response.data[0])

@api_router.get("/ogloszenia", response_model=List[Bus])
async def get_all_buses():
    """Get all bus listings (public endpoint)"""
    response = supabase.table('buses').select('*').execute()
    return [Bus(**bus) for bus in response.data]

@api_router.get("/ogloszenia/{bus_id}", response_model=Bus)
async def get_bus_by_id(bus_id: str):
    """Get a single bus listing by ID"""
    response = supabase.table('buses').select('*').eq('id', bus_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return Bus(**response.data[0])

@api_router.put("/ogloszenia/{bus_id}", response_model=Bus, dependencies=[Depends(admin_required)])
async def update_bus(bus_id: str, bus_update: BusUpdate):
    """Update a bus listing"""
    # Get existing bus
    response = supabase.table('buses').select('*').eq('id', bus_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in bus_update.dict().items() if v is not None}
    
    if update_data:
        response = supabase.table('buses').update(update_data).eq('id', bus_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update bus")
        
        return Bus(**response.data[0])
    
    # No updates, return existing
    return Bus(**response.data[0])

@api_router.delete("/ogloszenia/{bus_id}", dependencies=[Depends(admin_required)])
async def delete_bus(bus_id: str):
    """Delete a bus listing"""
    response = supabase.table('buses').delete().eq('id', bus_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return {"success": True, "message": "Bus deleted successfully"}

@api_router.get("/stats")
async def get_stats():
    """Get statistics for admin dashboard"""
    # Get all buses
    response = supabase.table('buses').select('*').execute()
    buses = response.data
    
    total = len(buses)
    wyrozniowane = sum(1 for b in buses if b.get('wyrozniowane'))
    nowe = sum(1 for b in buses if b.get('nowosc'))
    flotowe = sum(1 for b in buses if b.get('flotowy'))
    
    return {
        "total": total,
        "wyrozniowane": wyrozniowane,
        "nowe": nowe,
        "flotowe": flotowe
    }

# Opinion CRUD endpoints
@api_router.post("/opinie", response_model=Opinion, dependencies=[Depends(admin_required)])
async def create_opinion(opinion_data: OpinionCreate):
    """Create a new opinion"""
    opinion_dict = opinion_data.dict()
    opinion_id = str(uuid.uuid4())
    opinion_dict['id'] = opinion_id
    opinion_dict['dataPublikacji'] = datetime.now().isoformat()
    
    response = supabase.table('opinions').insert(opinion_dict).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create opinion")
    
    return Opinion(**response.data[0])

@api_router.get("/opinie", response_model=List[Opinion], dependencies=[Depends(admin_required)])
async def get_all_opinions():
    """Get all opinions (for admin)"""
    response = supabase.table('opinions').select('*').execute()
    return [Opinion(**opinion) for opinion in response.data]

@api_router.get("/opinie/public", response_model=List[Opinion])
async def get_public_opinions():
    """Get only visible opinions (for public page)"""
    response = supabase.table('opinions').select('*').eq('wyswietlaj', True).execute()
    # Sort by date, newest first
    opinions = [Opinion(**opinion) for opinion in response.data]
    return sorted(opinions, key=lambda x: x.dataPublikacji, reverse=True)

@api_router.get("/opinie/{opinion_id}", response_model=Opinion)
async def get_opinion_by_id(opinion_id: str):
    """Get a single opinion by ID"""
    response = supabase.table('opinions').select('*').eq('id', opinion_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Opinion not found")
    
    return Opinion(**response.data[0])

@api_router.put("/opinie/{opinion_id}", response_model=Opinion, dependencies=[Depends(admin_required)])
async def update_opinion(opinion_id: str, opinion_update: OpinionUpdate):
    """Update an opinion"""
    response = supabase.table('opinions').select('*').eq('id', opinion_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Opinion not found")
    
    update_data = {k: v for k, v in opinion_update.dict().items() if v is not None}
    
    if update_data:
        response = supabase.table('opinions').update(update_data).eq('id', opinion_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update opinion")
        
        return Opinion(**response.data[0])
    
    return Opinion(**response.data[0])

@api_router.delete("/opinie/{opinion_id}", dependencies=[Depends(admin_required)])
async def delete_opinion(opinion_id: str):
    """Delete an opinion"""
    response = supabase.table('opinions').delete().eq('id', opinion_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Opinion not found")
    
    return {"success": True, "message": "Opinion deleted successfully"}

# Admin login endpoints
@api_router.get(f"/admin-{ADMIN_PATH}", response_class=HTMLResponse)
async def admin_login_get_api():
    """Handle GET request to API endpoint - redirect to frontend login page"""
    return RedirectResponse(url=f"/admin-{ADMIN_PATH}", status_code=303)

@api_router.post(f"/admin-{ADMIN_PATH}")
async def admin_login_json(request: Request, login_data: AdminLoginRequest):
    """Handle admin login via JSON API (from React frontend)"""
    if (login_data.password or "").strip() != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Set cookie in response
    response = JSONResponse({
        "success": True,
        "message": "Login successful"
    })
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=_sign("ok"),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 8  # 8 hours
    )
    return response

# Include the router in the main app
app.include_router(api_router)

# Mount static files for local uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Serve frontend build (for production on Railway)
FRONTEND_BUILD_DIR = ROOT_DIR.parent / "frontend" / "build"
if FRONTEND_BUILD_DIR.exists():
    logger = logging.getLogger(__name__)
    logger.info(f"Frontend build directory found: {FRONTEND_BUILD_DIR}")
    
    # Mount static files from React build
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static-frontend")
    
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str, request: Request):
        """Serve React frontend for all non-API routes"""
        # Don't interfere with API routes or uploads
        if full_path.startswith("api") or full_path.startswith("uploads"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Handle root
        if not full_path or full_path == "/":
            return FileResponse(FRONTEND_BUILD_DIR / "index.html")
        
        # Try to serve the requested file
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        # Default to index.html for React routing (SPA)
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")
else:
    logger = logging.getLogger(__name__)
    logger.warning(f"Frontend build directory not found: {FRONTEND_BUILD_DIR}")

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
