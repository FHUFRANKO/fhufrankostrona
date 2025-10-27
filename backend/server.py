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
    # Nowe pola z Otomoto
    kolor: Optional[str] = None
    podwojneTylneKola: bool = False
    krajPochodzenia: Optional[str] = None
    numerRejestracyjny: Optional[str] = None
    stan: Optional[str] = None  # "Nowy" / "Używany"
    dataPierwszejRejestracji: Optional[str] = None
    bezwypadkowy: Optional[bool] = None
    maNumerRejestracyjny: Optional[bool] = None
    serwisowanyWAso: Optional[bool] = None
    # Wyposażenie
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
    winda: bool = False
    czterykola: bool = False
    hak: bool = False
    sold: bool = False  # Mapped from gwarancja
    reserved: bool = False  # Mapped from hak (workaround for schema cache issue)
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
    # Nowe pola
    kolor: Optional[str] = None
    krajPochodzenia: Optional[str] = None
    stan: Optional[str] = None
    bezwypadkowy: Optional[bool] = None
    # Wyposażenie
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
    # Nowe pola
    kolor: Optional[str] = None
    krajPochodzenia: Optional[str] = None
    stan: Optional[str] = None
    bezwypadkowy: Optional[bool] = None
    # Wyposażenie
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
    czterykola: Optional[bool] = None
    winda: Optional[bool] = None

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

class OtomotoScrapeRequest(BaseModel):
    url: str

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

# Scrape Otomoto endpoint
@api_router.post("/scrape-otomoto", dependencies=[Depends(admin_required)])
async def scrape_otomoto(request: OtomotoScrapeRequest):
    """Scrape vehicle data from Otomoto URL"""
    try:
        url = request.url.strip()
        
        # Validate URL
        if 'otomoto.pl' not in url:
            raise HTTPException(status_code=400, detail="Nieprawidłowy URL Otomoto")
        
        # Fetch page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract data
        data = {}
        missing_fields = []
        
        # Helper function to extract text
        def get_text(selector, default=""):
            elem = soup.select_one(selector)
            return elem.get_text(strip=True) if elem else default
        
        # Helper to extract from parameters list
        def get_param(label):
            params = soup.select('li.offer-params__item')
            for param in params:
                label_elem = param.select_one('.offer-params__label')
                value_elem = param.select_one('.offer-params__value, a')
                if label_elem and label in label_elem.get_text():
                    return value_elem.get_text(strip=True) if value_elem else None
            return None
        
        # Title (usually contains brand and model)
        title = get_text('h1.offer-title')
        if title:
            # Try to split brand and model
            parts = title.split()
            data['marka'] = parts[0] if parts else ""
            data['model'] = ' '.join(parts[1:]) if len(parts) > 1 else ""
        else:
            missing_fields.extend(['marka', 'model'])
        
        # Price
        price_text = get_text('.offer-price__number')
        if price_text:
            price_clean = re.sub(r'[^\d]', '', price_text)
            data['cenaBrutto'] = int(price_clean) if price_clean else None
        else:
            missing_fields.append('cenaBrutto')
        
        # Year
        year = get_param('Rok produkcji')
        data['rok'] = int(year) if year and year.isdigit() else None
        if not data.get('rok'):
            missing_fields.append('rok')
        
        # Mileage
        mileage = get_param('Przebieg')
        if mileage:
            mileage_clean = re.sub(r'[^\d]', '', mileage)
            data['przebieg'] = int(mileage_clean) if mileage_clean else None
        else:
            missing_fields.append('przebieg')
        
        # Fuel type
        fuel = get_param('Rodzaj paliwa')
        data['paliwo'] = fuel or ""
        if not fuel:
            missing_fields.append('paliwo')
        
        # Transmission
        transmission = get_param('Skrzynia biegów')
        data['skrzynia'] = transmission or ""
        if not transmission:
            missing_fields.append('skrzynia')
        
        # Power
        power = get_param('Moc')
        if power:
            power_match = re.search(r'(\d+)', power)
            data['moc'] = int(power_match.group(1)) if power_match else None
        else:
            missing_fields.append('moc')
        
        # Engine capacity
        capacity = get_param('Pojemność skokowa')
        if capacity:
            capacity_clean = re.sub(r'[^\d]', '', capacity)
            data['kubatura'] = int(capacity_clean) if capacity_clean else None
        
        # Emission standard
        emission = get_param('Emisja CO2')
        # Try to determine Euro standard
        if 'Euro 6' in str(soup) or 'EURO 6' in str(soup):
            data['normaEmisji'] = 'Euro 6'
        elif 'Euro 5' in str(soup) or 'EURO 5' in str(soup):
            data['normaEmisji'] = 'Euro 5'
        else:
            data['normaEmisji'] = 'Euro 6'  # Default
        
        # Body type - look for common terms
        body_type = get_param('Typ')
        if body_type:
            body_lower = body_type.lower()
            if 'furg' in body_lower:
                data['typNadwozia'] = 'Furgon'
            elif 'bus' in body_lower or 'mini' in body_lower:
                data['typNadwozia'] = 'Minibus'
            elif 'pod' in body_lower or 'skrzy' in body_lower:
                data['typNadwozia'] = 'Podwozie'
            else:
                data['typNadwozia'] = body_type
        else:
            data['typNadwozia'] = 'Furgon'  # Default
        
        # DMC category
        dmc = get_param('Dopuszczalna masa')
        if dmc:
            dmc_clean = re.sub(r'[^\d]', '', dmc)
            dmc_val = int(dmc_clean) if dmc_clean else 3500
            if dmc_val <= 3500:
                data['dmcKategoria'] = 'do 3.5t'
            else:
                data['dmcKategoria'] = 'powyżej 3.5t'
        else:
            data['dmcKategoria'] = 'do 3.5t'
        
        # Payload capacity (estimate)
        if data.get('dmcKategoria') == 'do 3.5t':
            data['ladownosc'] = 1000  # Default estimate
        else:
            data['ladownosc'] = 1500
        missing_fields.append('ladownosc (sprawdź dokładną wartość)')
        
        # Drive type
        drive = get_param('Napęd')
        if drive:
            if 'przód' in drive.lower() or 'FWD' in drive:
                data['naped'] = 'Przedni (FWD)'
            elif '4x4' in drive or 'AWD' in drive or 'wszystkie' in drive.lower():
                data['naped'] = '4x4 (AWD)'
            elif 'tył' in drive.lower() or 'RWD' in drive:
                data['naped'] = 'Tylni (RWD)'
        
        # Description
        desc = get_text('.offer-description__description')
        if desc and len(desc) > 50:
            data['opis'] = desc[:500]  # Limit to 500 chars
        
        # Features/Equipment
        wyposazenie = []
        
        # Check for common features in params
        if get_param('Klimatyzacja') or 'klimatyzacja' in str(soup).lower():
            wyposazenie.append('Klimatyzacja')
            data['klima'] = True
        
        if get_param('Tempomat') or 'tempomat' in str(soup).lower():
            wyposazenie.append('Tempomat')
            data['tempomat'] = True
        
        if 'kamera' in str(soup).lower() or 'camera' in str(soup).lower():
            wyposazenie.append('Kamera cofania')
            data['kamera'] = True
        
        if 'czujnik' in str(soup).lower() and 'park' in str(soup).lower():
            wyposazenie.append('Czujniki parkowania')
            data['czujnikiParkowania'] = True
        
        if 'hak' in str(soup).lower():
            wyposazenie.append('Hak holowniczy')
            data['hak'] = True
        
        data['wyposazenie'] = wyposazenie
        
        # === NOWE POLA ===
        
        # Kolor
        kolor = get_param('Kolor')
        if kolor:
            data['kolor'] = kolor
        else:
            missing_fields.append('kolor')
        
        # Kraj pochodzenia
        kraj = get_param('Kraj pochodzenia') or get_param('Pochodzenie')
        if kraj:
            data['krajPochodzenia'] = kraj
        elif 'pierwsza rejestracja w polsce' in str(soup).lower() or 'zarejestrowany w polsce' in str(soup).lower():
            data['krajPochodzenia'] = 'Polska'
        else:
            missing_fields.append('krajPochodzenia')
        
        # Stan (Nowy/Używany)
        stan_text = get_param('Stan')
        if stan_text:
            if 'now' in stan_text.lower():
                data['stan'] = 'Nowy'
            elif 'uży' in stan_text.lower() or 'używan' in stan_text.lower():
                data['stan'] = 'Używany'
            else:
                data['stan'] = stan_text
        else:
            # Try to guess from mileage
            if data.get('przebieg', 0) < 100:
                data['stan'] = 'Nowy'
            else:
                data['stan'] = 'Używany'
        
        # Bezwypadkowy
        if 'bezwypadkowy' in str(soup).lower():
            data['bezwypadkowy'] = True
        elif 'powypadkowy' in str(soup).lower() or 'uszkodzony' in str(soup).lower():
            data['bezwypadkowy'] = False
        else:
            missing_fields.append('bezwypadkowy (sprawdź w opisie)')
        
        # Fields that should be filled manually
        manual_fields = [
            'wymiarL (np. L2, L3)',
            'wymiarH (np. H2, H3)',
            'cenaNetto (jeśli dotyczy)',
            'liczbaMiejsc (jeśli dotyczy)',
            'liczbaPalet (jeśli dotyczy)',
            'normaSpalania',
            'gwarancja (ustaw checkbox)',
            'wyrozniowane (ustaw checkbox)',
            'nowosc (ustaw checkbox)',
            'flotowy (ustaw checkbox)'
        ]
        
        missing_fields.extend(manual_fields)
        
        return {
            "success": True,
            "data": data,
            "missing_fields": missing_fields,
            "message": "Dane pobrane z Otomoto. Sprawdź i uzupełnij brakujące pola."
        }
        
    except requests.RequestException as e:
        logger.error(f"Otomoto scrape error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Nie udało się pobrać danych z Otomoto: {str(e)}")
    except Exception as e:
        logger.error(f"Otomoto parse error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Błąd parsowania danych: {str(e)}")


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
    # Map gwarancja to sold and hak to reserved (workaround)
    buses = []
    for bus_data in response.data:
        bus_data['sold'] = bus_data.get('gwarancja', False)
        bus_data['reserved'] = bus_data.get('hak', False)
        buses.append(Bus(**bus_data))
    return buses

@api_router.get("/ogloszenia/{bus_id}", response_model=Bus)
async def get_bus_by_id(bus_id: str):
    """Get a single bus listing by ID"""
    response = supabase.table('buses').select('*').eq('id', bus_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Map gwarancja to sold and hak to reserved (workaround)
    bus_data = response.data[0]
    bus_data['sold'] = bus_data.get('gwarancja', False)
    bus_data['reserved'] = bus_data.get('hak', False)
    return Bus(**bus_data)

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

@api_router.get("/admin/check-auth")
async def check_auth(user: dict = Depends(get_current_user_optional)):
    """Check if user is authenticated as admin"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True, "user": user}

@api_router.post("/ogloszenia/{bus_id}/toggle-sold", dependencies=[Depends(admin_required)])
async def toggle_sold_status(bus_id: str):
    """Toggle sold status for a bus listing (using gwarancja field as workaround)"""
    # Get current bus
    response = supabase.table('buses').select('*').eq('id', bus_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    bus_data = response.data[0]
    current_sold = bus_data.get('gwarancja', False)
    new_sold = not current_sold
    
    # First update the sold status (gwarancja)
    response = supabase.table('buses').update({'gwarancja': new_sold}).eq('id', bus_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update sold status")
    
    # If setting to sold=True, make sure reserved=False (mutually exclusive) - separate update
    reserved_status = bus_data.get('hak', False)
    if new_sold and reserved_status:
        # Need to set reserved to False (using hak)
        response2 = supabase.table('buses').update({'hak': False}).eq('id', bus_id).execute()
        if response2.data:
            reserved_status = False
    
    return {"success": True, "sold": new_sold, "reserved": reserved_status}

@api_router.post("/ogloszenia/{bus_id}/toggle-reserved", dependencies=[Depends(admin_required)])
async def toggle_reserved_status(bus_id: str):
    """Toggle reserved status for a bus listing (using hak field as workaround)"""
    # Get current bus first
    get_response = supabase.table('buses').select('*').eq('id', bus_id).execute()
    
    if not get_response.data:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    bus_data = get_response.data[0]
    current_reserved = bus_data.get('hak', False)
    new_reserved = not current_reserved
    
    # Prepare update data
    update_fields = {'hak': new_reserved}
    if new_reserved:
        # If setting reserved=True, make sure sold=False (mutually exclusive)
        update_fields['gwarancja'] = False
    
    # Use the existing update logic that works
    try:
        response = supabase.table('buses').update(update_fields).eq('id', bus_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update reserved status")
        
        updated_bus = response.data[0]
        return {
            "success": True, 
            "reserved": updated_bus.get('hak', False), 
            "sold": updated_bus.get('gwarancja', False)
        }
    except Exception as e:
        # Fallback: try updating fields separately
        try:
            # First update hak
            response1 = supabase.table('buses').update({'hak': new_reserved}).eq('id', bus_id).execute()
            if not response1.data:
                raise HTTPException(status_code=500, detail="Failed to update reserved status")
            
            # Then update gwarancja if needed
            sold_status = bus_data.get('gwarancja', False)
            if new_reserved and sold_status:
                response2 = supabase.table('buses').update({'gwarancja': False}).eq('id', bus_id).execute()
                if response2.data:
                    sold_status = False
            
            return {"success": True, "reserved": new_reserved, "sold": sold_status}
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Failed to update reserved status: {str(e2)}")

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

# ========== NEW LISTING SYSTEM ENDPOINTS ==========
# Import new listing models
from listing_models import Listing, ListingCreate, ListingUpdate, FuelType, GearboxType, ConditionStatus
from pydantic import ValidationError

def map_listing_to_bus_db(listing_data: dict) -> dict:
    """Map new listing model fields to existing database schema"""
    bus_data = {
        # Map title explicitly
        'title': listing_data.get('title'),
        
        # SEKCJA 1: Informacje podstawowe
        'marka': listing_data.get('make'),
        'model': listing_data.get('model'),
        'color': listing_data.get('color'),
        'liczbaMiejsc': listing_data.get('seats'),
        'rok': listing_data.get('production_year'),
        'vin': listing_data.get('vin'),
        'installments_available': listing_data.get('installments_available', False),
        'cenaBrutto': listing_data.get('price_pln'),
        
        # SEKCJA 2: Specyfikacja techniczna
        'paliwo': listing_data.get('fuel_type'),
        'kubatura': listing_data.get('engine_displacement_cc'),
        'moc': listing_data.get('power_hp'),
        'typNadwozia': listing_data.get('body_type'),
        'skrzynia': listing_data.get('gearbox'),
        'gvw_kg': listing_data.get('gvw_kg'),
        'twin_rear_wheels': listing_data.get('twin_rear_wheels', False),
        
        # SEKCJA 3: Stan i historia pojazdu
        'origin_country': listing_data.get('origin_country'),
        'przebieg': listing_data.get('mileage_km'),
        'registration_number': listing_data.get('registration_number'),
        'condition_status': listing_data.get('condition_status'),
        'first_registration_date': listing_data.get('first_registration_date').isoformat() if listing_data.get('first_registration_date') else None,
        'accident_free': listing_data.get('accident_free', False),
        'has_registration_number': listing_data.get('has_registration_number', False),
        'serviced_in_aso': listing_data.get('serviced_in_aso', False),
        
        # SEKCJA 4: Opis sprzedawcy
        'description_html': listing_data.get('description_html'),
        'opis': listing_data.get('description_html'),  # Keep both for backward compatibility
        'home_delivery': listing_data.get('home_delivery', False),
        'tech_visual_short': listing_data.get('tech_visual_short'),
        'seller_profile_url': listing_data.get('seller_profile_url'),
        'location_street': listing_data.get('location_street'),
        'location_city': listing_data.get('location_city'),
        'location_region': listing_data.get('location_region'),
        
        # Additional fields
        'zdjecia': listing_data.get('zdjecia', []),
        'zdjecieGlowne': listing_data.get('zdjecieGlowne'),
        'wyrozniowane': listing_data.get('wyrozniowane', False),
        'nowosc': listing_data.get('nowosc', False),
        'flotowy': listing_data.get('flotowy', False),
        'gwarancja': listing_data.get('sold', False),  # SOLD mapped to gwarancja
        'sold': listing_data.get('sold', False),
        
        # Required fields with defaults for backward compatibility
        'normaEmisji': 'Euro 6',
        'dmcKategoria': 'do 3.5t',
        'ladownosc': 1000,
        'vat': True,
    }
    
    # Remove None values
    return {k: v for k, v in bus_data.items() if v is not None}

def map_bus_db_to_listing(bus_data: dict) -> dict:
    """Map database fields to new listing model"""
    return {
        # SEKCJA 1
        'title': bus_data.get('title') or f"{bus_data.get('marka', '')} {bus_data.get('model', '')}".strip(),
        'price_pln': bus_data.get('cenaBrutto'),
        'make': bus_data.get('marka'),
        'model': bus_data.get('model'),
        'color': bus_data.get('color'),
        'seats': bus_data.get('liczbaMiejsc'),
        'production_year': bus_data.get('rok'),
        'vin': bus_data.get('vin'),
        'installments_available': bus_data.get('installments_available', False),
        
        # SEKCJA 2
        'fuel_type': bus_data.get('paliwo'),
        'engine_displacement_cc': bus_data.get('kubatura'),
        'power_hp': bus_data.get('moc'),
        'body_type': bus_data.get('typNadwozia'),
        'gearbox': bus_data.get('skrzynia'),
        'gvw_kg': bus_data.get('gvw_kg'),
        'twin_rear_wheels': bus_data.get('twin_rear_wheels', False),
        
        # SEKCJA 3
        'origin_country': bus_data.get('origin_country'),
        'mileage_km': bus_data.get('przebieg'),
        'registration_number': bus_data.get('registration_number'),
        'condition_status': bus_data.get('condition_status') or 'Używany',
        'first_registration_date': bus_data.get('first_registration_date'),
        'accident_free': bus_data.get('accident_free', False),
        'has_registration_number': bus_data.get('has_registration_number', False),
        'serviced_in_aso': bus_data.get('serviced_in_aso', False),
        
        # SEKCJA 4
        'description_html': bus_data.get('description_html') or bus_data.get('opis') or '',
        'home_delivery': bus_data.get('home_delivery', False),
        'tech_visual_short': bus_data.get('tech_visual_short'),
        'seller_profile_url': bus_data.get('seller_profile_url'),
        'location_street': bus_data.get('location_street'),
        'location_city': bus_data.get('location_city'),
        'location_region': bus_data.get('location_region'),
        
        # System fields
        'id': bus_data.get('id'),
        'created_at': bus_data.get('created_at') or bus_data.get('dataPublikacji'),
        'updated_at': bus_data.get('updated_at'),
        
        # Additional
        'zdjecia': bus_data.get('zdjecia', []),
        'zdjecieGlowne': bus_data.get('zdjecieGlowne'),
        'wyrozniowane': bus_data.get('wyrozniowane', False),
        'nowosc': bus_data.get('nowosc', False),
        'flotowy': bus_data.get('flotowy', False),
        'gwarancja': bus_data.get('gwarancja', False),
        'sold': bus_data.get('gwarancja', False),  # SOLD mapped from gwarancja
    }

@api_router.post("/admin/listings", dependencies=[Depends(admin_required)])
async def create_listing(listing_data: ListingCreate):
    """Create a new listing with new validation system"""
    try:
        # Convert listing model to database schema
        listing_dict = listing_data.dict()
        bus_dict = map_listing_to_bus_db(listing_dict)
        
        # Generate ID
        bus_id = str(uuid.uuid4())
        bus_dict['id'] = bus_id
        bus_dict['dataPublikacji'] = datetime.now().isoformat()
        bus_dict['created_at'] = datetime.now().isoformat()
        
        # Generate listing number
        response = supabase.table('buses').select('id', count='exact').execute()
        count = response.count if hasattr(response, 'count') else len(response.data)
        bus_dict['numerOgloszenia'] = f"FKBUS{str(count + 1).zfill(6)}"
        
        # Insert into database
        response = supabase.table('buses').insert(bus_dict).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Nie udało się utworzyć ogłoszenia")
        
        # Map back to listing format
        listing_response = map_bus_db_to_listing(response.data[0])
        
        return {
            "success": True,
            "data": listing_response,
            "message": "Ogłoszenie utworzone pomyślnie"
        }
        
    except ValidationError as e:
        # Return detailed validation errors in Polish
        errors = {}
        for error in e.errors():
            field = error['loc'][-1]
            message = error['msg']
            errors[field] = message
        
        raise HTTPException(
            status_code=422,
            detail={
                "errors": errors,
                "message": "Błędy walidacji"
            }
        )
    except Exception as e:
        logger.error(f"Create listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Błąd tworzenia ogłoszenia: {str(e)}")

@api_router.put("/admin/listings/{listing_id}", dependencies=[Depends(admin_required)])
async def update_listing(listing_id: str, listing_update: ListingUpdate):
    """Update an existing listing"""
    try:
        # Check if listing exists
        response = supabase.table('buses').select('*').eq('id', listing_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Ogłoszenie nie znalezione")
        
        # Convert update to database schema
        update_dict = {k: v for k, v in listing_update.dict().items() if v is not None}
        if update_dict:
            bus_update = map_listing_to_bus_db(update_dict)
            bus_update['updated_at'] = datetime.now().isoformat()
            
            response = supabase.table('buses').update(bus_update).eq('id', listing_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Nie udało się zaktualizować ogłoszenia")
        
        # Return updated listing
        listing_response = map_bus_db_to_listing(response.data[0])
        
        return {
            "success": True,
            "data": listing_response,
            "message": "Ogłoszenie zaktualizowane pomyślnie"
        }
        
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            field = error['loc'][-1]
            message = error['msg']
            errors[field] = message
        
        raise HTTPException(
            status_code=422,
            detail={
                "errors": errors,
                "message": "Błędy walidacji"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update listing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Błąd aktualizacji ogłoszenia: {str(e)}")

@api_router.get("/admin/listings/{listing_id}")
async def get_listing(listing_id: str, user: dict = Depends(get_current_user_optional)):
    """Get a single listing by ID (admin-only for full data)"""
    response = supabase.table('buses').select('*').eq('id', listing_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Ogłoszenie nie znalezione")
    
    listing_response = map_bus_db_to_listing(response.data[0])
    
    return {
        "success": True,
        "data": listing_response
    }

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
    
    # Mount static files from React build (only if static directory exists)
    static_dir = FRONTEND_BUILD_DIR / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static-frontend")
    
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
