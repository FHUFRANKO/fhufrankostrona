from datetime import datetime, timedelta, timezone
import re as regex_cron
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import httpx
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
    return hmac.new(
        ADMIN_COOKIE_SECRET.encode(),
        value.encode(),
        hashlib.sha256).hexdigest()


# Supabase client (database + storage)
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_bucket = os.environ.get('SUPABASE_BUCKET', 'bus-images')

if not supabase_url or not supabase_key:
    logging.error("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    logging.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

MOCK_BUSES = []
MOCK_OPINIONS = []

# --- AUTH START ---
oauth2_scheme = HTTPBearer(auto_error=False)
JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET', '')
ADMIN_EMAILS = set(
    e.strip().lower() for e in os.environ.get(
        'ADMIN_EMAILS',
        '').split(',') if e.strip())


def verify_supabase_token(token: str) -> dict:
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
    cookie_token = request.cookies.get(ADMIN_COOKIE_NAME)
    if cookie_token == _sign("ok"):
        return {
            "email": "admin@cookie",
            "auth_method": "cookie",
            "admin": True}

    if creds and JWT_SECRET:
        try:
            payload = verify_supabase_token(creds.credentials)
            return {**payload, "auth_method": "jwt"}
        except BaseException:
            pass
    return None


def admin_required(user: Optional[dict] = Depends(get_current_user_optional)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if user.get("auth_method") == "cookie":
        return user

    if user.get("auth_method") == "jwt":
        email = (user.get('email') or '').lower()
        if email not in ADMIN_EMAILS:
            raise HTTPException(
                status_code=403,
                detail=f"Admin access required. Email '{email}' is not in admin list.")
        return user

    raise HTTPException(status_code=403, detail="Admin access required")
# --- AUTH END ---


app = FastAPI()

@app.middleware("http")
async def _admin_guard(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/admin"):
        token = request.cookies.get(ADMIN_COOKIE_NAME)
        if token == _sign("ok"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            pass
        else:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    response = await call_next(request)
    return response

api_router = APIRouter(prefix="/api")

class AdminLoginRequest(BaseModel):
    password: str

class OtomotoScrapeRequest(BaseModel):
    url: str

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
        'normaEmisji': 'Euro 6',
        'dmcKategoria': 'do 3.5t',
        'ladownosc': 1000,
        'vat': True,
    }
    if listing_data.get('title'):
        bus_data['naped'] = listing_data.get('title')
    return {k: v for k, v in bus_data.items() if v is not None}


def map_bus_db_to_listing(bus_data: dict) -> dict:
    result = dict(bus_data)
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
    result['zdjecia'] = bus_data.get('zdjecia') or []
    result['wyposazenie'] = bus_data.get('wyposazenie') or {}

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
    
    # --- WYMUSZENIE WIDOCZNOŚCI DLA FRONTENDU ---
    is_sold_val = bool(bus_data.get('gwarancja') or bus_data.get('sold'))
    result['status'] = 'aktywne' # Nigdy nie zmieniaj na 'sprzedane', bo React ukryje auto!
    result['sold'] = is_sold_val
    result['gwarancja'] = is_sold_val
    
    is_reserved_val = bool(bus_data.get('hak') or bus_data.get('reserved'))
    result['reserved'] = is_reserved_val
    result['hak'] = is_reserved_val
    return result

# --- API ENDPOINTS ---

@api_router.get("/")
async def read_root():
    return {"status": "ok", "message": "FHU FRANKO API"}

@api_router.post("/auth/login")
async def login(request: Request, login_data: AdminLoginRequest):
    if login_data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    response = JSONResponse({"success": True, "message": "Login successful", "user": {"email": "admin", "admin": True}})
    response.set_cookie(key=ADMIN_COOKIE_NAME, value=_sign("ok"), httponly=True, secure=True, samesite="lax", max_age=60*60*24*7)
    return response

@api_router.post("/auth/logout")
async def logout():
    response = JSONResponse({"success": True, "message": "Logged out"})
    response.delete_cookie(ADMIN_COOKIE_NAME)
    return response

@api_router.get("/admin/check-auth")
async def check_auth(user: Optional[dict] = Depends(get_current_user_optional)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True, "user": user}

@api_router.get("/ogloszenia")
async def get_all_listings():
    response = supabase.table('buses').select('*').execute()
    listings = [map_bus_db_to_listing(bus) for bus in response.data]
    listings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return listings

@api_router.get("/ogloszenia/{listing_id}")
async def get_listing_by_id(listing_id: str):
    response = supabase.table('buses').select('*').eq('id', listing_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    return map_bus_db_to_listing(response.data[0])

@api_router.post("/admin/listings", dependencies=[Depends(admin_required)])
async def create_listing(listing_data: ListingCreate):
    try:
        bus_dict = map_listing_to_bus_db(listing_data.dict())
        import uuid
        import random
        from datetime import datetime
        bus_dict['id'] = str(uuid.uuid4())
        bus_dict['dataPublikacji'] = datetime.now().isoformat()
        bus_dict['numerOgloszenia'] = f"FKBUS{random.randint(100000, 999999)}"
        defaults = {
            'marka': 'Inna', 'model': 'Inny', 'rok': 2000, 'przebieg': 0, 'cenaBrutto': 0,
            'paliwo': 'Diesel', 'skrzynia': 'Manualna', 'typNadwozia': 'Furgon', 'moc': 0,
            'miasto': 'Smyków', 'normaEmisji': 'Euro 6', 'dmcKategoria': 'do 3.5t', 'ladownosc': 1000, 'vat': True,
            'status': 'aktywne'
        }
        for k, v in defaults.items():
            if bus_dict.get(k) is None:
                bus_dict[k] = v
        response = supabase.table('buses').insert(bus_dict).execute()
        return {"success": True, "data": bus_dict, "message": "Ogłoszenie utworzone pomyślnie"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd Supabase: {str(e)}")

@api_router.put("/admin/listings/{listing_id}", dependencies=[Depends(admin_required)])
async def update_listing(listing_id: str, listing_update: ListingUpdate):
    try:
        update_dict = {k: v for k, v in listing_update.dict().items() if v is not None}
        if update_dict:
            bus_update = map_listing_to_bus_db(update_dict)
            response = supabase.table('buses').update(bus_update).eq('id', listing_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Database update failed")
            return {"success": True, "data": map_bus_db_to_listing(response.data[0]), "message": "Zaktualizowano"}
        return {"success": True, "message": "No changes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/ogloszenia/{listing_id}", dependencies=[Depends(admin_required)])
async def legacy_update_listing(listing_id: str, request: Request):
    """Zabezpieczony endpoint aktualizacji (stara metoda PUT) z filtrowaniem kolumn"""
    try:
        data = await request.json()
        from datetime import datetime, timezone
        
        update_data = {}
        VALID_COLUMNS = {
            'marka', 'model', 'rok', 'przebieg', 'cenaBrutto', 'paliwo', 'skrzynia',
            'typNadwozia', 'moc', 'kubatura', 'kolor', 'opis', 'zdjecia', 'zdjecieGlowne',
            'wyrozniowane', 'nowosc', 'flotowy', 'gwarancja', 'hak', 'miasto',
            'pierwszaRejestracja', 'vin', 'normaEmisji', 'dmcKategoria', 'ladownosc',
            'vat', 'naped', 'status', 'data_sprzedazy', 'dmc', 'krajPochodzenia', 'stan',
            'liczbaMiejsc', 'numerOgloszenia'
        }
        
        for k, v in data.items():
            if k in VALID_COLUMNS:
                update_data[k] = v
                
        if 'gwarancja' in data or 'sold' in data or data.get('status') == 'sprzedane':
            is_sold = bool(data.get('gwarancja') or data.get('sold') or data.get('status') == 'sprzedane')
            update_data['gwarancja'] = is_sold
            update_data['status'] = 'aktywne'  # Nigdy nie chowamy aut
            update_data['data_sprzedazy'] = datetime.now(timezone.utc).isoformat() if is_sold else None
            
        if 'hak' in data or 'reserved' in data:
            update_data['hak'] = bool(data.get('hak') or data.get('reserved'))

        if 'id' in update_data:
            del update_data['id']

        if update_data:
            response = supabase.table('buses').update(update_data).eq('id', listing_id).execute()
            if not response.data:
                raise HTTPException(status_code=404, detail="Nie znaleziono ogłoszenia")
            
            return {"success": True, "data": map_bus_db_to_listing(response.data[0])}
            
        return {"success": True, "message": "Brak zmian"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/admin/listings/{listing_id}", dependencies=[Depends(admin_required)])
async def delete_listing(listing_id: str):
    listing = supabase.table('buses').select('zdjecia, zdjecieGlowne').eq('id', listing_id).execute()
    response = supabase.table('buses').delete().eq('id', listing_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Listing not found")
    try:
        if listing.data:
            bus = listing.data[0]
            images = bus.get('zdjecia', []) or []
            main_image = bus.get('zdjecieGlowne')
            if main_image and main_image not in images:
                images.append(main_image)
            paths_to_delete = [img.split('/')[-1] for img in images if "Client.co" in img and "/buses/" in img]
            if paths_to_delete:
                supabase.storage.from_("buses").remove([f"buses/{p}" for p in paths_to_delete])
    except Exception as e:
        logging.warning(f"Nie usunięto zdjęć: {e}")
    return {"success": True, "message": "Usunięto"}

@api_router.post("/admin/listings/{bus_id}/toggle-sold", dependencies=[Depends(admin_required)])
@api_router.post("/ogloszenia/{bus_id}/toggle-sold", dependencies=[Depends(admin_required)])
async def toggle_sold(bus_id: str):
    try:
        from datetime import datetime, timezone
        bus_req = supabase.table('buses').select('*').eq('id', bus_id).execute()
        if not bus_req.data: raise HTTPException(404, "Nie znaleziono")
        
        new_state = not bool(bus_req.data[0].get('gwarancja'))
        update_data = {
            'gwarancja': new_state,
            'status': 'aktywne',
            'data_sprzedazy': datetime.now(timezone.utc).isoformat() if new_state else None
        }
        
        resp = supabase.table('buses').update(update_data).eq('id', bus_id).execute()
        mapped = map_bus_db_to_listing(resp.data[0])
        return {"success": True, "sold": new_state, "data": mapped}
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@api_router.post("/admin/listings/{bus_id}/toggle-reserved", dependencies=[Depends(admin_required)])
@api_router.post("/ogloszenia/{bus_id}/toggle-reserved", dependencies=[Depends(admin_required)])
async def toggle_reserved(bus_id: str):
    try:
        bus = supabase.table('buses').select('hak').eq('id', bus_id).execute()
        if not bus.data:
            raise HTTPException(404, "Not found")
        current = bus.data[0].get('hak', False)
        new_val = not current
        response = supabase.table('buses').update({'hak': new_val}).eq('id', bus_id).execute()
        mapped = map_bus_db_to_listing(response.data[0])
        return {"success": True, "reserved": new_val, "data": mapped}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@api_router.post("/upload", dependencies=[Depends(admin_required)])
async def upload_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        try:
            path = f"buses/{filename}"
            supabase.storage.from_("buses").upload(path, contents, file_options={"content-type": file.content_type})
            public_url = supabase.storage.from_("buses").get_public_url(path)
            return {"success": True, "url": public_url}
        except Exception:
            local_path = UPLOADS_DIR / "buses"
            local_path.mkdir(parents=True, exist_ok=True)
            with open(local_path / filename, "wb") as f:
                f.write(contents)
            return {"success": True, "url": f"/uploads/buses/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/upload-bulk", dependencies=[Depends(admin_required)])
async def upload_images_bulk(files: List[UploadFile] = File(...)):
    uploaded_urls = []
    errors = []
    MAX_FILE_SIZE = 10 * 1024 * 1024
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/avif"]
    for file in files:
        try:
            if file.content_type not in ALLOWED_TYPES: continue
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE: continue
            ext = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            path = f"buses/{unique_filename}"
            supabase.storage.from_("buses").upload(path, contents, file_options={"content-type": file.content_type})
            public_url = supabase.storage.from_("buses").get_public_url(path)
            uploaded_urls.append(public_url)
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    return {"success": True if len(uploaded_urls) > 0 else False, "urls": uploaded_urls, "errors": errors}

# --- ODZYSKANY RĘCZNY SCRAPER OTOMOTO ---
@api_router.post("/scrape-otomoto", dependencies=[Depends(admin_required)])
async def scrape_otomoto_endpoint(request: OtomotoScrapeRequest):
    import json
    import re
    try:
        url = request.url.strip()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pl-PL,pl;q=0.9",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15)

        if response.status_code in [403, 401, 429]:
            raise Exception("Otomoto zablokowało zapytanie (Ochrona Cloudflare).")

        response.raise_for_status()

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
            if m_title:
                data["title"] = m_title.group(1)

        m_price = re.search(r'"price"[\s:]*\{[^}]*?"value"[\s:]*(\d+)', html)
        if m_price:
            data["cenaBrutto"] = int(m_price.group(1))

        try:
            import re as regex_yt
            yt_link = ""
            iframe = soup.find('iframe', src=regex_yt.compile(r'youtube\.com|youtu\.be'))
            if iframe: yt_link = iframe.get('src', '')
            if not yt_link:
                yt_match = regex_yt.search(r'(https://www\.youtube\.com/watch\?v=[\w-]+|https://youtu\.be/[\w-]+)', str(soup))
                if yt_match: yt_link = yt_match.group(0)
            if yt_link:
                yt_link = yt_link.replace('embed/', 'watch?v=')
                data['youtube'] = yt_link
                data['youtubeLink'] = yt_link
                data['video'] = yt_link
        except Exception as e:
            pass
        else:
            p_elem = soup.select_one('[data-testid="ad-price-container"] h3') or soup.find('h3', class_=lambda c: c and 'price' in str(c).lower())
            if not p_elem: p_elem = soup.find(attrs={"data-testid": "ad-price-container"})
            if p_elem: data["cenaBrutto"] = int(re.sub(r'[^\d]', '', (p_elem.text if p_elem else " ")))

        raw_images = re.findall(r'"(https://[^"]+\.olxcdn\.com/[^"]+)"', html)
        hq_images = [img.split(';')[0] + ";s=1080x720" for img in raw_images if "image" in img]
        unique_images = list(dict.fromkeys(hq_images))
        if unique_images:
            data["zdjecia"] = unique_images
            data["zdjecieGlowne"] = unique_images[0]

        desc_elem = soup.select_one('[data-testid="ad-description"]') or soup.select_one('.offer-description__description')
        if desc_elem:
            for br in desc_elem.find_all("br"): br.replace_with("\n")
            for p in desc_elem.find_all("p"): p.append("\n")
            clean_text = (desc_elem.text if desc_elem else " ")
            clean_text = re.sub(r' {2,}', ' ', clean_text)
            clean_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_text)
            data["opis"] = clean_text.strip()
        else:
            m_desc = re.search(r'"description"[\s:]*"(.*?)"(?:,|})', html)
            if m_desc:
                try: data["opis"] = json.loads('"' + m_desc.group(1) + '"')
                except BaseException: data["opis"] = m_desc.group(1)

        for k in ["rok", "przebieg", "moc", "kubatura"]:
            if data.get(k):
                try:
                    v = str(data[k]).lower().replace('cm3', '').replace('cm³', '')
                    data[k] = int(re.sub(r'[^\d]', '', v))
                except BaseException:
                    pass

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
        raise HTTPException(status_code=500, detail=f"Błąd krytyczny: {str(e)}")


@api_router.get("/admin/stats", dependencies=[Depends(admin_required)])
async def get_stats():
    response = supabase.table('buses').select('*').execute()
    buses = response.data
    return {
        "total": len(buses),
        "wyrozniowane": sum(1 for b in buses if b.get('wyrozniowane')),
        "nowe": sum(1 for b in buses if b.get('nowosc')),
        "flotowe": sum(1 for b in buses if b.get('flotowy'))
    }

@api_router.get("/opinie")
async def get_opinions():
    response = supabase.table('opinions').select('*').eq('wyswietlaj', True).execute()
    return response.data

@api_router.get("/admin/opinions", dependencies=[Depends(admin_required)])
async def get_all_opinions_admin():
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

app.include_router(api_router)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

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

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

async def upload_image_task(img_url, supabase_client):
    try:
        async with httpx.AsyncClient() as client:
            img_r = await client.get(img_url, timeout=10)
            if img_r.status_code == 200:
                fname = f"{uuid.uuid4()}.jpg"
                supabase_client.storage.from_("buses").upload(
                    f"buses/{fname}",
                    img_r.content,
                    file_options={"content-type": "image/jpeg"}
                )
                return supabase_client.storage.from_("buses").get_public_url(f"buses/{fname}")
    except Exception as e:
        print(f"[CRON] Błąd uploadu zdjęcia ({img_url}): {e}")
    return None

# --- ODZYSKANY CRON OTOMOTO ---
async def sync_otomoto_job():
    print("[CRON] Automatyczne pobieranie z Otomoto zostało zablokowane na życzenie.")
    return # <--- TA JEDNA LINIJKA WYŁĄCZA AUTOMATYCZNE POBIERANIE NOWYCH AUT!
    
    if not supabase: return
    try:
        db_resp = supabase.table('buses').select('*').execute()
        db_buses = db_resp.data or []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pl-PL,pl;q=0.9",
        }
        offer_links = set()

        async with httpx.AsyncClient() as client:
            for page in range(1, 4):
                try:
                    resp = await client.get(f"{DEALER_URL}?page={page}", headers=headers, timeout=15)
                    soup = BeautifulSoup(resp.content, "html.parser")
                    links = [a['href'].split('?')[0] for a in soup.find_all('a', href=True) if '/oferta/' in a['href'] and 'otomoto.pl' in a['href']]
                    if not links: break
                    for l in links: offer_links.add(l)
                except Exception as e:
                     pass

            active_vins = set()
            active_titles = set()

            for link in offer_links:
                try:
                    r = await client.get(link, headers=headers, timeout=15)
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
                                except BaseException:
                                    pass

                        marka = extract_oto_value(html, "make", "Marka pojazdu") or title.split()[0] if title else "Inna"
                        model = extract_oto_value(html, "model", "Model pojazdu") or "Inny"

                        raw_images = regex_cron.findall(r'"(https://[^"]+\.olxcdn\.com/[^"]+)"', html)
                        hq_images = [img.split(';')[0] + ";s=1080x720" for img in raw_images if "image" in img]
                        unique_images = list(dict.fromkeys(hq_images))

                        if data.get('cenaBrutto', 0) <= 0 or not unique_images:
                            continue

                        upload_tasks = [upload_image_task(url, supabase) for url in unique_images[:10]]
                        uploaded_results = await asyncio.gather(*upload_tasks)
                        uploaded_urls = [url for url in uploaded_results if url]

                        desc_elem = BeautifulSoup(html, "html.parser").select_one('[data-testid="ad-description"]')
                        if desc_elem:
                            for br in desc_elem.find_all("br"): br.replace_with("\n")
                            opis = str(getattr(desc_elem, "text", "Zaimportowano automatycznie.") or "Zaimportowano automatycznie.")
                        else:
                            opis = "Zaimportowano automatycznie."

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
                    pass
                await asyncio.sleep(2)

        for bus in db_buses:
            if bus.get('status') == 'sprzedane':
                if bus.get('data_sprzedazy'):
                    try:
                        dt_str = bus['data_sprzedazy'].replace('Z', '+00:00')
                        sell_date = datetime.fromisoformat(dt_str)
                        if datetime.now(timezone.utc) - sell_date > timedelta(days=5):
                            supabase.table('buses').delete().eq('id', bus['id']).execute()
                            images = bus.get('zdjecia', [])
                            paths = [img.split('/')[-1] for img in images if "Client.co" in img]
                            if paths: supabase.storage.from_("buses").remove([f"buses/{p}" for p in paths])
                    except BaseException:
                        pass
            else:
                is_missing = False
                if bus.get('vin') and len(bus.get('vin')) > 5:
                    if bus.get('vin') not in active_vins: is_missing = True
                else:
                    if bus.get('naped') and bus.get('naped') not in active_titles: is_missing = True

                if is_missing and active_vins:
                    supabase.table('buses').update({
                        'status': 'aktywne', # Zawsze zostaje aktywne!
                        'gwarancja': True, 
                        'data_sprzedazy': datetime.now(timezone.utc).isoformat()
                    }).eq('id', bus['id']).execute()
    except Exception as e:
        pass


@app.on_event("startup")
async def start_otomoto_cron():
    print("[CRON] Automatyczne skanowanie Otomoto jest bezpiecznie uśpione.")
    try:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(sync_otomoto_job, 'interval', minutes=60)
        scheduler.start()
    except Exception as e:
        pass