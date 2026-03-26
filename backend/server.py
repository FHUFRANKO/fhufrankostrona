import requests
import traceback
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from pathlib import Path
from datetime import datetime, date
import os
import hmac
import hashlib
import logging
import uuid
import jwt
import cloudscraper
from bs4 import BeautifulSoup
import re
from supabase import create_client, Client

# Import new listing models
from listing_models import Listing, ListingCreate, ListingUpdate, FuelType, GearboxType, ConditionStatus

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create uploads directory
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Admin Configuration
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
    # Ensure variables are set, otherwise fail gracefully or log error
    logging.error("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    logging.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

# Mock data for when Supabase is missing
MOCK_BUSES = [
    {
        "id": "mock-1",
        "marka": "Renault",
        "model": "Master",
        "rok": 2019,
        "przebieg": 185000,
        "cenaBrutto": 65900,
        "paliwo": "Diesel",
        "typNadwozia": "Furgon (blaszak)",
        "zdjecia": [],
        "wyrozniowane": True,
        "opis": "Przykładowe ogłoszenie (Brak połączenia z bazą danych)",
        "dataPublikacji": datetime.now().isoformat()
    }
]
MOCK_OPINIONS = []

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

async def get_current_user_optional(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    """Get current user from JWT or cookie session"""
    # Try cookie first (password-based admin access)
    cookie_token = request.cookies.get(ADMIN_COOKIE_NAME)
    if cookie_token == _sign("ok"):
        return {"email": "admin@cookie", "auth_method": "cookie", "admin": True}
    
    # Try JWT token
    if creds and JWT_SECRET:
        try:
            payload = verify_supabase_token(creds.credentials)
            return {**payload, "auth_method": "jwt"}
        except:
            pass
    
    return None

def admin_required(user: Optional[dict] = Depends(get_current_user_optional)):
    """Dependency to require admin privileges (cookie or JWT)"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
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

# Admin Panel Guard Middleware for API routes
@app.middleware("http")
async def _admin_guard(request: Request, call_next):
    """Protect /api/admin* routes"""
    path = request.url.path
    
    if path.startswith("/api/admin"):
        # Check cookie
        token = request.cookies.get(ADMIN_COOKIE_NAME)
        if token == _sign("ok"):
            return await call_next(request)
            
        # Check Authorization header (JWT)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Let the dependency handle JWT validation
            pass
        else:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    
    response = await call_next(request)
    return response

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# --- MODELS ---
# (Using Listing models mostly, but keeping simplified ones for compatibility if needed)
class AdminLoginRequest(BaseModel):
    password: str

class OtomotoScrapeRequest(BaseModel):
    url: str

class Opinion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    imie: str
    nazwisko: str = ""
    rodzajFirmy: str = ""
    opinia: str = Field(alias="komentarz")
    zakupionyPojazd: str = ""
    ocena: int = 5
    wyswietlaj: bool = True
    dataPublikacji: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        populate_by_name = True

class OpinionCreate(BaseModel):
    imie: str
    nazwisko: Optional[str] = ""
    rodzajFirmy: Optional[str] = ""
    opinia: str = Field(alias="komentarz")
    zakupionyPojazd: Optional[str] = ""
    ocena: int = 5
    wyswietlaj: bool = True

class OpinionUpdate(BaseModel):
    imie: Optional[str] = None
    nazwisko: Optional[str] = None
    rodzajFirmy: Optional[str] = None
    opinia: Optional[str] = Field(None, alias="komentarz")
    zakupionyPojazd: Optional[str] = None
    ocena: Optional[int] = None
    wyswietlaj: Optional[bool] = None

# --- HELPERS ---
def map_listing_to_bus_db(listing_data: dict) -> dict:
    """Map new listing model fields STRICTLY to existing database schema"""
    bus_data = {
        'marka': listing_data.get('make'),
        'model': listing_data.get('model'),
        'rok': listing_data.get('production_year'),
        'przebieg': listing_data.get('mileage_km'),
        'cenaBrutto': listing_data.get('price_pln'),
        'paliwo': listing_data.get('fuel_type'),
        'skrzynia': listing_data.get('gearbox'),
        'typNadwozia': listing_data.get('body_type'),
        'moc': listing_data.get('power_hp'),
        'kubatura': listing_data.get('engine_displacement_cc'),
        'kolor': listing_data.get('color'),
        'opis': listing_data.get('description_html'),
        'zdjecia': listing_data.get('zdjecia', []),
        'zdjecieGlowne': listing_data.get('zdjecieGlowne') or (listing_data.get('zdjecia')[0] if listing_data.get('zdjecia') else None),
        
        'wyrozniowane': listing_data.get('wyrozniowane', False),
        'nowosc': listing_data.get('nowosc', False),
        'flotowy': listing_data.get('flotowy', False),
        'gwarancja': listing_data.get('sold', False), 
        'hak': listing_data.get('reserved', False),   
        
        'miasto': listing_data.get('location_city', 'Smyków'),
        'pierwszaRejestracja': str(listing_data.get('first_registration_date'))[:10] if listing_data.get('first_registration_date') else None,
        'vin': listing_data.get('vin'),
        
        # Pola wymagane przez baze do ktorych nie mamy wejscia w nowym UI
        'normaEmisji': 'Euro 6',
        'dmcKategoria': 'do 3.5t',
        'ladownosc': 1000,
        'vat': True,
    }
    
    # Hack: przechowujemy wygenerowany na nowo Tytuł w starym polu "naped", 
    # zeby stara tabela bazy danych go nie odrzuciła
    if listing_data.get('title'):
        bus_data['naped'] = listing_data.get('title')
        
    return {k: v for k, v in bus_data.items() if v is not None}

def map_bus_db_to_listing(bus_data: dict) -> dict:
    """Map database fields to new listing model while preserving legacy frontend keys"""
    # Kopiujemy oryginalne dane z bazy
    result = dict(bus_data)
    
    # 1. Odtworzenie POLSKICH kluczy (dla publicznej strony głównej)
    result['cenaBrutto'] = bus_data.get('cenaBrutto') or bus_data.get('price_pln')
    result['rok'] = bus_data.get('rok') or bus_data.get('production_year')
    result['przebieg'] = bus_data.get('przebieg') or bus_data.get('mileage_km')
    result['marka'] = bus_data.get('marka') or bus_data.get('make')
    result['paliwo'] = bus_data.get('paliwo') or bus_data.get('fuel_type')
    result['skrzynia'] = bus_data.get('skrzynia') or bus_data.get('gearbox')
    result['moc'] = bus_data.get('moc') or bus_data.get('power_hp')
    result['kubatura'] = bus_data.get('kubatura') or bus_data.get('engine_displacement_cc')
    result['typNadwozia'] = bus_data.get('typNadwozia') or bus_data.get('body_type')
    result['opis'] = bus_data.get('opis') or bus_data.get('description_html')
    
    # Zabezpieczenia dla list i obiektów (zapobiega crashom "Cannot read properties of undefined")
    result['zdjecia'] = bus_data.get('zdjecia') or []
    result['wyposazenie'] = bus_data.get('wyposazenie') or {}

    # 2. Odtworzenie ANGIELSKICH kluczy (dla nowego Panelu Admina)
    result['title'] = bus_data.get('title') or f"{result.get('marka', '')} {bus_data.get('model', '')}".strip()
    result['price_pln'] = result['cenaBrutto']
    result['make'] = result['marka']
    result['production_year'] = result['rok']
    result['mileage_km'] = result['przebieg']
    result['fuel_type'] = result['paliwo']
    result['gearbox'] = result['skrzynia']
    result['power_hp'] = result['moc']
    result['engine_displacement_cc'] = result['kubatura']
    result['body_type'] = result['typNadwozia']
    result['description_html'] = result['opis']
    
    result['color'] = bus_data.get('kolor') or bus_data.get('color')
    result['seats'] = bus_data.get('liczbaMiejsc') or bus_data.get('seats')
    result['gvw_kg'] = bus_data.get('dmc') or bus_data.get('gvw_kg')
    result['origin_country'] = bus_data.get('krajPochodzenia') or bus_data.get('origin_country')
    result['condition_status'] = bus_data.get('stan') or bus_data.get('condition_status') or 'Używany'
    
    return result

# --- API ENDPOINTS ---

@api_router.get("/")
async def read_root():
    """Health check endpoint"""
    return {"status": "ok", "message": "FHU FRANKO API"}

# Auth Endpoints
@api_router.post("/auth/login")
async def login(request: Request, login_data: AdminLoginRequest):
    """Admin login with password"""
    if login_data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    response = JSONResponse({
        "success": True,
        "message": "Login successful",
        "user": {"email": "admin", "admin": True}
    })
    
    # Set secure cookie
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=_sign("ok"),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 days
    )
    return response

@api_router.post("/auth/logout")
async def logout():
    """Admin logout"""
    response = JSONResponse({"success": True, "message": "Logged out"})
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response

@api_router.get("/admin/check-auth")
async def check_auth(user: Optional[dict] = Depends(get_current_user_optional)):
    """Check if user is authenticated"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True, "user": user}

# Listing Endpoints (Public)
@api_router.get("/ogloszenia")
async def get_all_listings():
    """Get all listings (public)"""
    if not supabase:
        return [map_bus_db_to_listing(bus) for bus in MOCK_BUSES]
        
    response = supabase.table('buses').select('*').execute()
    listings = [map_bus_db_to_listing(bus) for bus in response.data]
    # Sort by created_at desc
    listings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return listings

@api_router.get("/ogloszenia/{listing_id}")
async def get_listing_by_id(listing_id: str):
    """Get single listing (public)"""
    if not supabase:
        bus = next((b for b in MOCK_BUSES if b['id'] == listing_id), None)
        if not bus:
            raise HTTPException(status_code=404, detail="Listing not found")
        return map_bus_db_to_listing(bus)

    response = supabase.table('buses').select('*').eq('id', listing_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    return map_bus_db_to_listing(response.data[0])

# Admin Listing Endpoints
@api_router.post("/admin/listings", dependencies=[Depends(admin_required)])
async def create_listing(listing_data: ListingCreate):
    """Create new listing safely"""
    try:
        bus_dict = map_listing_to_bus_db(listing_data.dict())
        
        import uuid
        import random
        from datetime import datetime
        
        bus_id = str(uuid.uuid4())
        bus_dict['id'] = bus_id
        bus_dict['dataPublikacji'] = datetime.now().isoformat()
        
        # Zamiast liczyć wpisy w bazie (co powodowało crashe), 
        # generujemy bezpieczny, losowy numer ogłoszenia.
        bus_dict['numerOgloszenia'] = f"FKBUS{random.randint(100000, 999999)}"
        
        # Twarde domyślne wartości dla kolumn bazy, aby Postgres nie odrzucił zapisu
        defaults = {
            'marka': 'Inna', 'model': 'Inny', 'rok': 2000, 'przebieg': 0, 'cenaBrutto': 0,
            'paliwo': 'Diesel', 'skrzynia': 'Manualna', 'typNadwozia': 'Furgon', 'moc': 0,
            'miasto': 'Smyków', 'normaEmisji': 'Euro 6', 'dmcKategoria': 'do 3.5t',
            'ladownosc': 1000, 'vat': True
        }
        for k, v in defaults.items():
            if bus_dict.get(k) is None:
                bus_dict[k] = v
        
        response = supabase.table('buses').insert(bus_dict).execute()
        
        return {
            "success": True,
            "data": bus_dict,
            "message": "Ogłoszenie utworzone pomyślnie"
        }
    except Exception as e:
                logging.error(f"Create error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Błąd Supabase: {str(e)}")

@api_router.put("/admin/listings/{listing_id}", dependencies=[Depends(admin_required)])
async def update_listing(listing_id: str, listing_update: ListingUpdate):
    """Update listing"""
    try:
        # Check existence
        response = supabase.table('buses').select('*').eq('id', listing_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Listing not found")
            
        # Prepare update data
        update_dict = {k: v for k, v in listing_update.dict().items() if v is not None}
        
        if update_dict:
            bus_update = map_listing_to_bus_db(update_dict)
            
            
            # Remove keys that shouldn't be updated if they are mapped incorrectly or empty
            # map_listing_to_bus_db might add defaults, we should be careful.
            # Actually map_listing_to_bus_db does a full mapping.
            # Better to only map fields that were present in update_dict.
            # But map_listing_to_bus_db expects full structure roughly.
            # Let's trust the mapping but filter out None from the result of mapping if origin was not in update_dict? 
            # No, map_listing_to_bus_db uses .get() so it handles partials if we pass partial dict?
            # Yes, if we pass partial dict to map_listing_to_bus_db, it will return fields.
            
            response = supabase.table('buses').update(bus_update).eq('id', listing_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Database update failed")
                
            return {
                "success": True,
                "data": map_bus_db_to_listing(response.data[0]),
                "message": "Ogłoszenie zaktualizowane"
            }
            
        return {"success": True, "message": "No changes detected"}
        
    except Exception as e:
        logging.error(f"Update listing error: {e}")
        raise HTTPException(status_code=500, detail=f"Błąd bazy Supabase: {str(e)}")

@api_router.delete("/admin/listings/{listing_id}", dependencies=[Depends(admin_required)])
async def delete_listing(listing_id: str):
    """Delete listing and its images"""
    # Najpierw pobieramy dane, aby wiedzieć jakie zdjęcia usunąć z chmury
    listing = supabase.table('buses').select('zdjecia, zdjecieGlowne').eq('id', listing_id).execute()
    
    # 1. Usuwamy wpis z bazy danych
    response = supabase.table('buses').delete().eq('id', listing_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
        
    # 2. Próbujemy usunąć zdjęcia z Supabase Storage (optymalizacja miejsca)
    try:
        if listing.data:
            bus = listing.data[0]
            images = bus.get('zdjecia', []) or []
            main_image = bus.get('zdjecieGlowne')
            if main_image and main_image not in images:
                images.append(main_image)
                
            paths_to_delete = []
            for img_url in images:
                if img_url and "Client.co" in img_url and "/buses/" in img_url:
                    # Wyciągamy samą nazwę pliku po ostatnim ukośniku
                    filename = img_url.split('/')[-1]
                    paths_to_delete.append(f"buses/{filename}")
            
            if paths_to_delete:
                supabase.storage.from_("buses").remove(paths_to_delete)
    except Exception as e:
        logging.warning(f"Nie udało się usunąć zdjęć z chmury: {e}")

    return {"success": True, "message": "Ogłoszenie i zdjęcia usunięte"}

# Upload Image
@api_router.post("/upload", dependencies=[Depends(admin_required)])
async def upload_image(file: UploadFile = File(...)):
    """Upload image to Supabase or local"""
    try:
        contents = await file.read()
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        
        # Try Supabase
        try:
            path = f"buses/{filename}"
            supabase.storage.from_("buses").upload(path, contents, file_options={"content-type": file.content_type})
            public_url = supabase.storage.from_("buses").get_public_url(path)
            return {"success": True, "url": public_url}
        except Exception as e:
            logging.warning(f"Supabase upload failed, falling back to local: {e}")
            
            # Local fallback
            local_path = UPLOADS_DIR / "buses"
            local_path.mkdir(parents=True, exist_ok=True)
            with open(local_path / filename, "wb") as f:
                f.write(contents)
            return {"success": True, "url": f"/uploads/buses/{filename}"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@api_router.post("/upload-bulk", dependencies=[Depends(admin_required)])
async def upload_images_bulk(files: List[UploadFile] = File(...)):
    """Upload multiple images to Supabase Storage in one request"""
    uploaded_urls = []
    errors = []
    
    MAX_FILE_SIZE = 10 * 1024 * 1024 
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/avif"]

    for file in files:
        try:
            if file.content_type not in ALLOWED_TYPES:
                errors.append(f"{file.filename}: Niewłaściwy format (Tylko JPG/PNG/WEBP/AVIF)")
                continue
                
            contents = await file.read()
            
            if len(contents) > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: Plik za duży (Max 10MB)")
                continue

            ext = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            
            try:
                path = f"buses/{unique_filename}"
                supabase.storage.from_("buses").upload(path, contents, file_options={"content-type": file.content_type})
                public_url = supabase.storage.from_("buses").get_public_url(path)
                uploaded_urls.append(public_url)
            except Exception as supabase_error:
                logging.warning(f"Supabase upload failed, using local fallback: {supabase_error}")
                local_path = UPLOADS_DIR / "buses"
                local_path.mkdir(parents=True, exist_ok=True)
                with open(local_path / unique_filename, "wb") as local_f:
                    local_f.write(contents)
                uploaded_urls.append(f"/uploads/buses/{unique_filename}")
            
        except Exception as e:
            errors.append(f"{file.filename}: Błąd uploadu ({str(e)})")

    return {
        "success": True if len(uploaded_urls) > 0 else False,
        "urls": uploaded_urls,
        "errors": errors
    }

# Otomoto Scraper
@api_router.post("/scrape-otomoto", dependencies=[Depends(admin_required)])
async def scrape_otomoto_endpoint(request: OtomotoScrapeRequest):
    """Otomoto Scraper - Ostateczny Fix na Kodowanie (Czysty tekst + UTF-8)"""
    import json
    import re
    try:
        url = request.url.strip()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pl-PL,pl;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code in [403, 401, 429]:
            raise Exception("Otomoto zablokowało zapytanie (Ochrona Cloudflare).")
            
        response.raise_for_status()
        
        # Wymuszamy czytanie surowych bajtów jako UTF-8
        html = response.content.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        data = {}
        
        def extract_value(key, label):
            m = re.search(r'"key"[\s:]*"' + key + r'"[^}]*?"displayValue"[\s:]*"([^"]+)"', html)
            if m: return m.group(1)
            m = re.search(r'"key"[\s:]*"' + key + r'"[^}]*?"value"[\s:]*"([^"]+)"', html)
            if m: return m.group(1)
            m = re.search(r'"label"[\s:]*"' + label + r'"[^}]*?"value"[\s:]*"([^"]+)"', html)
            if m: return m.group(1)
            
            m2 = re.search(label + r'[^>]*?>([a-zA-Z0-9\sęóąśłżźćńĘÓĄŚŁŻŹĆŃ]+)<', html)
            if m2:
                val = m2.group(1).strip()
                if len(val) < 40 and val != label: return val
            return None

        data["rok"] = extract_value("year", "Rok produkcji")
        data["przebieg"] = extract_value("mileage", "Przebieg")
        data["moc"] = extract_value("engine_power", "Moc")
        data["kubatura"] = extract_value("engine_capacity", "Pojemność skokowa")
        data["vin"] = extract_value("vin", "VIN")
        if data.get("vin") and ("Zgadzam" in str(data["vin"]) or len(str(data["vin"])) > 20):
            data["vin"] = ""
            for div in soup.find_all('div', attrs={"data-testid": "advert-details-item"}):
                p_tags = div.find_all('p')
                if len(p_tags) >= 2 and "VIN" in p_tags[0].text:
                    data["vin"] = p_tags[1].text.strip()

        data["marka"] = extract_value("make", "Marka pojazdu")
        data["model"] = extract_value("model", "Model pojazdu")
        data["wersja"] = extract_value("version", "Wersja")
        data["paliwo"] = extract_value("fuel_type", "Rodzaj paliwa")
        data["skrzynia"] = extract_value("gearbox", "Skrzynia biegów")
        data["typNadwozia"] = extract_value("body_type", "Typ nadwozia")
        data["kolor"] = extract_value("color", "Kolor")
        data["krajPochodzenia"] = extract_value("country_origin", "Kraj pochodzenia")
        
        data["bezwypadkowy"] = extract_value("no_accident", "Bezwypadkowy") == "Tak"
        data["serwisowanyWAso"] = extract_value("service_record", "Serwisowany w ASO") == "Tak"
        data["maNumerRejestracyjny"] = extract_value("registered", "Zarejestrowany w Polsce") == "Tak"

        title_elem = soup.select_one("h1")
        if title_elem:
            data["title"] = (title_elem.text if title_elem else " ")
        else:
            m_title = re.search(r'"title"[\s:]*"([^"]+)"', html)
            if m_title: data["title"] = m_title.group(1)

        m_price = re.search(r'"price"[\s:]*\{[^}]*?"value"[\s:]*(\d+)', html)
        if m_price:
            data["cenaBrutto"] = int(m_price.group(1))

        # --- POBIERANIE LINKU YOUTUBE ---
        try:
            import re as regex_yt
            yt_link = ""
            
            # Opcja 1: Szukanie wprost iframe z YouTube
            iframe = soup.find('iframe', src=regex_yt.compile(r'youtube\.com|youtu\.be'))
            if iframe:
                yt_link = iframe.get('src', '')
            
            # Opcja 2: Przeszukanie ukrytych stanów strony (Otomoto często trzyma tam wideo)
            if not yt_link:
                yt_match = regex_yt.search(r'(https://www\.youtube\.com/watch\?v=[\w-]+|https://youtu\.be/[\w-]+)', str(soup))
                if yt_match:
                    yt_link = yt_match.group(0)

            if yt_link:
                yt_link = yt_link.replace('embed/', 'watch?v=')
                # Przypisujemy pod kilkoma najpopularniejszymi nazwami zmiennych:
                data['youtube'] = yt_link
                data['youtubeLink'] = yt_link
                data['video'] = yt_link
        except Exception as e:
            print("Błąd pobierania YT:", e)
        else:
            p_elem = soup.select_one('[data-testid="ad-price-container"] h3') or soup.find('h3', class_=lambda c: c and 'price' in str(c).lower())
            if not p_elem:
                p_elem = soup.find(attrs={"data-testid": "ad-price-container"})
            if p_elem: 
                data["cenaBrutto"] = int(re.sub(r'[^\d]', '', (p_elem.text if p_elem else " ")))

        raw_images = re.findall(r'"(https://[^"]+\.olxcdn\.com/[^"]+)"', html)
        hq_images = []
        for img in raw_images:
            if "image" in img:
                base = img.split(';')[0]
                hq_images.append(base + ";s=1080x720")
                
        unique_images = list(dict.fromkeys(hq_images))
        if unique_images:
            data["zdjecia"] = unique_images
            data["zdjecieGlowne"] = unique_images[0]

        # 5. OPIS - Wymuszanie przerw między liniami
        desc_elem = soup.select_one('[data-testid="ad-description"]') or soup.select_one('.offer-description__description')
        if desc_elem:
            for br in desc_elem.find_all("br"):
                br.replace_with("\n")
            for p in desc_elem.find_all("p"):
                p.append("\n")
                
            clean_text = (desc_elem.text if desc_elem else " ")
            clean_text = re.sub(r' {2,}', ' ', clean_text)
            clean_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_text)
            data["opis"] = clean_text.strip()
        else:
            m_desc = re.search(r'"description"[\s:]*"(.*?)"(?:,|})', html)
            if m_desc:
                try:
                    data["opis"] = json.loads('"' + m_desc.group(1) + '"')
                except:
                    data["opis"] = m_desc.group(1)

        for k in ["rok", "przebieg", "moc", "kubatura"]:
            if data.get(k):
                try:
                    v = str(data[k]).lower().replace('cm3', '').replace('cm³', '')
                    data[k] = int(re.sub(r'[^\d]', '', v))
                except: pass

        fuel = str(data.get("paliwo", "")).lower()
        if "diesel" in fuel: data["paliwo"] = "Diesel"
        elif "benz" in fuel or "petrol" in fuel: data["paliwo"] = "Benzyna"
        elif "elektry" in fuel or "electric" in fuel: data["paliwo"] = "Elektryczny"
        elif "hybry" in fuel: data["paliwo"] = "Hybryda"
        
        gb = str(data.get("skrzynia", "")).lower()
        if "auto" in gb: data["skrzynia"] = "Automatyczna"
        elif "man" in gb: data["skrzynia"] = "Manualna"

        if not data.get("marka") and data.get("title"):
            parts = data["title"].split()
            data["marka"] = parts[0]
            data["model"] = " ".join(parts[1:3])

        return {"success": True, "data": data, "missing_fields": []}
        
    except Exception as e:
                logging.error(f"Scrape error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Błąd krytyczny: {str(e)}")


@api_router.post("/ogloszenia/{bus_id}/toggle-sold", dependencies=[Depends(admin_required)])
async def toggle_sold(bus_id: str):
    bus = supabase.table('buses').select('gwarancja').eq('id', bus_id).execute()
    if not bus.data: raise HTTPException(404, "Not found")
    current = bus.data[0].get('gwarancja', False)
    supabase.table('buses').update({'gwarancja': not current}).eq('id', bus_id).execute()
    return {"success": True, "sold": not current}

@api_router.post("/ogloszenia/{bus_id}/toggle-reserved", dependencies=[Depends(admin_required)])
async def toggle_reserved(bus_id: str):
    bus = supabase.table('buses').select('hak').eq('id', bus_id).execute()
    if not bus.data: raise HTTPException(404, "Not found")
    current = bus.data[0].get('hak', False)
    supabase.table('buses').update({'hak': not current}).eq('id', bus_id).execute()
    return {"success": True, "reserved": not current}

# Stats Endpoint
@api_router.get("/admin/stats", dependencies=[Depends(admin_required)])
async def get_stats():
    if not supabase:
        return {
            "total": len(MOCK_BUSES),
            "wyrozniowane": sum(1 for b in MOCK_BUSES if b.get('wyrozniowane')),
            "nowe": sum(1 for b in MOCK_BUSES if b.get('nowosc')),
            "flotowe": sum(1 for b in MOCK_BUSES if b.get('flotowy'))
        }
    response = supabase.table('buses').select('*').execute()
    buses = response.data
    return {
        "total": len(buses),
        "wyrozniowane": sum(1 for b in buses if b.get('wyrozniowane')),
        "nowe": sum(1 for b in buses if b.get('nowosc')),
        "flotowe": sum(1 for b in buses if b.get('flotowy'))
    }

# Opinion Endpoints
@api_router.get("/opinie")
async def get_opinions():
    if not supabase:
        return MOCK_OPINIONS
    response = supabase.table('opinions').select('*').eq('wyswietlaj', True).execute()
    return response.data

@api_router.get("/admin/opinions", dependencies=[Depends(admin_required)])
async def get_all_opinions_admin():
    if not supabase:
        return MOCK_OPINIONS
    response = supabase.table('opinions').select('*').execute()
    return response.data

@api_router.post("/admin/opinions", dependencies=[Depends(admin_required)])
async def create_opinion(op: OpinionCreate):
    data = op.dict(by_alias=True)
    data['id'] = str(uuid.uuid4())
    data['dataPublikacji'] = datetime.now().isoformat()
    resp = supabase.table('opinions').insert(data).execute()
    return resp.data[0]

@api_router.put("/admin/opinions/{op_id}", dependencies=[Depends(admin_required)])
async def update_opinion(op_id: str, op: OpinionUpdate):
    data = {k: v for k, v in op.dict(by_alias=True).items() if v is not None}
    if data:
        resp = supabase.table('opinions').update(data).eq('id', op_id).execute()
        return resp.data[0]
    return {}

@api_router.delete("/admin/opinions/{op_id}", dependencies=[Depends(admin_required)])
async def delete_opinion(op_id: str):
    supabase.table('opinions').delete().eq('id', op_id).execute()
    return {"success": True}

# Register Router
app.include_router(api_router)

# Mount Uploads
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Frontend Static Files (if build exists)
FRONTEND_BUILD_DIR = ROOT_DIR.parent / "frontend" / "build"
if FRONTEND_BUILD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_BUILD_DIR / "static")), name="static-frontend")
    
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("uploads"):
            raise HTTPException(status_code=404)
        
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
            
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- AUTOMATYZACJA OTOMOTO ---
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
import cloudscraper
import re as regex_cron
from datetime import datetime, timedelta, timezone
import uuid

DEALER_URL = "https://fhufranko.otomoto.pl/inventory"

def extract_oto_value(html, key, label):
    m = regex_cron.search(r'"key"[\s:]*"' + key + r'"[^}]*?"displayValue"[\s:]*"([^"]+)"', html)
    if m: return m.group(1)
    m = regex_cron.search(r'"key"[\s:]*"' + key + r'"[^}]*?"value"[\s:]*"([^"]+)"', html)
    if m: return m.group(1)
    m = regex_cron.search(r'"label"[\s:]*"' + label + r'"[^}]*?"value"[\s:]*"([^"]+)"', html)
    if m: return m.group(1)
    m2 = regex_cron.search(label + r'[^>]*?>([a-zA-Z0-9\sęóąśłżźćńĘÓĄŚŁŻŹĆŃ]+)<', html)
    if m2:
        val = m2.group(1).strip()
        if len(val) < 40 and val != label: return val
    return None

async def sync_otomoto_job():
    print("[CRON] Rozpoczynam synchronizację z Otomoto...")
    if not supabase: return

    try:
        db_resp = supabase.table('buses').select('*').execute()
        db_buses = db_resp.data or []
        
        headers = {"User-Agent": "Mozilla/5.0"}
        offer_links = set()
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        
        # Pobieramy do 3 stron (dla pewności, że złapiemy wszystkie auta, jeśli jest ich więcej niż 30)
        for page in range(1, 4):
            resp = requests.get(f"{DEALER_URL}?page={page}", headers=headers, timeout=15)
            soup = BeautifulSoup(resp.content, "html.parser")
            links = [a['href'].split('?')[0] for a in soup.find_all('a', href=True) if '/oferta/' in a['href'] and 'otomoto.pl' in a['href']]
            if not links: break
            for l in links: offer_links.add(l)
                
        print(f"[CRON] Znaleziono {len(offer_links)} aktywnych linków na profilu Otomoto.")
        
        active_vins = set()
        active_titles = set()
        
        for link in offer_links:
            try:
                r = scraper.get(link, timeout=10)
                html = r.content.decode('utf-8', errors='ignore')
                
                vin = extract_oto_value(html, "vin", "VIN")
                if vin and ("Zgadzam" in vin or len(vin) > 20):
                    vin = ""
                    s_soup = BeautifulSoup(html, "html.parser")
                    for div in s_soup.find_all('div', attrs={"data-testid": "advert-details-item"}):
                        p_tags = div.find_all('p')
                        if len(p_tags) >= 2 and "VIN" in p_tags[0].text:
                            vin = p_tags[1].text.strip()
                
                m_title = regex_cron.search(r'"title"[\s:]*"([^"]+)"', html)
                title = m_title.group(1) if m_title else ""
                
                if vin: active_vins.add(vin)
                if title: active_titles.add(title)
                
                exists = False
                if vin:
                    exists = any(b.get('vin') == vin for b in db_buses)
                else:
                    m_price = regex_cron.search(r'"price"[\s:]*\{[^}]*?"value"[\s:]*(\d+)', html)
                    price = int(m_price.group(1)) if m_price else 0
                    exists = any((b.get('title') == title or b.get('naped') == title) and b.get('cenaBrutto') == price for b in db_buses)
                
                if not exists:
                    print(f"[CRON] Znaleziono nowe auto: {title}. Pobieram z Otomoto i dodaję do bazy Supabase...")
                    data = {"vin": vin, "title": title}
                    
                    price_elem = BeautifulSoup(html, "html.parser").select_one('[data-testid="ad-price-container"] h3')
                    if price_elem:
                        data["cenaBrutto"] = int(regex_cron.sub(r'[^\d]', '', str(getattr(price_elem, "text", "0") or "0")) or 0)
                    else:
                        m_price = regex_cron.search(r'"price"[\s:]*\{[^}]*?"value"[\s:]*(\d+)', html)
                        data["cenaBrutto"] = int(m_price.group(1)) if m_price else 0
                        
                    data["rok"] = extract_oto_value(html, "year", "Rok produkcji")
                    data["przebieg"] = extract_oto_value(html, "mileage", "Przebieg")
                    data["moc"] = extract_oto_value(html, "engine_power", "Moc")
                    data["kubatura"] = extract_oto_value(html, "engine_capacity", "Pojemność skokowa")
                    
                    for k in ["rok", "przebieg", "moc", "kubatura"]:
                        if data.get(k):
                            try:
                                v = str(data[k]).lower().replace('cm3', '').replace('cm³', '')
                                data[k] = int(regex_cron.sub(r'[^\d]', '', v))
                            except: pass
                            
                    marka = extract_oto_value(html, "make", "Marka pojazdu") or title.split()[0] if title else "Inna"
                    model = extract_oto_value(html, "model", "Model pojazdu") or "Inny"
                    
                    raw_images = regex_cron.findall(r'"(https://[^"]+\.olxcdn\.com/[^"]+)"', html)
                    hq_images = [img.split(';')[0] + ";s=1080x720" for img in raw_images if "image" in img]
                    unique_images = list(dict.fromkeys(hq_images))
                    
                    # Automatyczny upload zdjęć na Supabase
                    uploaded_urls = []
                    for img_url in unique_images[:10]: # Pobieramy maksymalnie pierwszych 10 zdjęć do optymalizacji
                        try:
                            img_r = requests.get(img_url, timeout=5)
                            fname = f"{uuid.uuid4()}.jpg"
                            supabase.storage.from_("buses").upload(f"buses/{fname}", img_r.content, file_options={"content-type": "image/jpeg"})
                            uploaded_urls.append(supabase.storage.from_("buses").get_public_url(f"buses/{fname}"))
                        except: pass
                            
                    desc_elem = BeautifulSoup(html, "html.parser").select_one('[data-testid="ad-description"]')
                    if desc_elem:
                        for br in desc_elem.find_all("br"): br.replace_with("\n")
                        opis = str(getattr(desc_elem, "text", "Zaimportowano automatycznie.") or "Zaimportowano automatycznie.")
                    else:
                        opis = "Zaimportowano automatycznie."
                        
                    # Zabezpieczający wpis z uzupełnieniem domyślnych kluczy, by PostgreSQL nie narzekał
                    bus_dict = {
                        'id': str(uuid.uuid4()),
                        'numerOgloszenia': f"FKBUS{str(uuid.uuid4().int)[:6]}",
                        'marka': marka,
                        'model': model,
                        'rok': data.get('rok', 2000),
                        'przebieg': data.get('przebieg', 0),
                        'cenaBrutto': data.get('cenaBrutto', 0),
                        'paliwo': extract_oto_value(html, "fuel_type", "Rodzaj paliwa") or "Diesel",
                        'skrzynia': extract_oto_value(html, "gearbox", "Skrzynia biegów") or "Manualna",
                        'typNadwozia': extract_oto_value(html, "body_type", "Typ nadwozia") or "Furgon",
                        'moc': data.get('moc', 0),
                        'kubatura': data.get('kubatura', 0),
                        'kolor': extract_oto_value(html, "color", "Kolor") or "Biały",
                        'opis': opis,
                        'zdjecia': uploaded_urls,
                        'zdjecieGlowne': uploaded_urls[0] if uploaded_urls else None,
                        'vin': data.get('vin'),
                        'naped': title,
                        'miasto': 'Smyków',
                        'status': 'aktywne',
                        'dataPublikacji': datetime.now(timezone.utc).isoformat(),
                        'normaEmisji': 'Euro 6',
                        'dmcKategoria': 'do 3.5t',
                        'ladownosc': 1000,
                        'vat': True
                    }
                    supabase.table('buses').insert(bus_dict).execute()
                    
            except Exception as e:
                print(f"[CRON] Błąd przy analizie oferty: {e}"); traceback.print_exc()
            await asyncio.sleep(2) # Odstęp, żeby Otomoto nie zablokowało serwera (zbyt dużo zapytań naraz)
            
        # 3. Oznacz jako sprzedane i usuwaj trwale stare ogłoszenia
        for bus in db_buses:
            if bus.get('status') == 'sprzedane':
                if bus.get('data_sprzedazy'):
                    try:
                        dt_str = bus['data_sprzedazy'].replace('Z', '+00:00')
                        sell_date = datetime.fromisoformat(dt_str)
                        if datetime.now(timezone.utc) - sell_date > timedelta(days=5):
                            print(f"[CRON] Auto {bus['id']} ma status sprzedanego powyżej 5 dni. Usuwam trwale.")
                            supabase.table('buses').delete().eq('id', bus['id']).execute()
                            # Usuwanie plików z koszyka zdjęć
                            images = bus.get('zdjecia', [])
                            paths = [img.split('/')[-1] for img in images if "Client.co" in img]
                            if paths: supabase.storage.from_("buses").remove([f"buses/{p}" for p in paths])
                    except: pass
            else:
                is_missing = False
                if bus.get('vin') and len(bus.get('vin')) > 5:
                    if bus.get('vin') not in active_vins: is_missing = True
                else:
                    if bus.get('naped') and bus.get('naped') not in active_titles: is_missing = True
                
                # Upewniamy się, że active_vins nie jest pusty (czyli że połączyliśmy się w ogóle z Otomoto) by uniknąć fałszywego usuwania
                if is_missing and active_vins:
                    print(f"[CRON] Auto zniknęło z profilu dealera na Otomoto. Oznaczam auto z bazy ({bus.get('id')}) jako sprzedane.")
                    supabase.table('buses').update({
                        'status': 'sprzedane',
                        'sold': True,
                        'gwarancja': True, # W starym UI pole to włączało widoczność etykietki
                        'data_sprzedazy': datetime.now(timezone.utc).isoformat()
                    }).eq('id', bus['id']).execute()

    except Exception as e:
        print(f"[CRON] Błąd główny pętli: {e}")

@app.on_event("startup")
async def start_otomoto_cron():
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(sync_otomoto_job, 'interval', minutes=30)
        scheduler.start()
        print("[CRON] Wymuszam pierwsze natychmiastowe skanowanie zaraz po starcie serwera!")
        asyncio.create_task(sync_otomoto_job())
        print("[CRON] Pomyślnie uruchomiono skaner. Automatyzacja działa w tle co 30 min.")
    except Exception as e:
        print("[CRON] Błąd uruchamiania schedulera:", e)
