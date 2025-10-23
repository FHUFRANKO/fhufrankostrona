"""
Pydantic models for new listing system
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
import uuid

from validators import (
    validate_vin,
    validate_url,
    validate_registration_number,
    validate_production_year,
    validate_first_registration_date,
    validate_price,
    validate_mileage,
    validate_seats,
    validate_engine_displacement,
    validate_power,
    validate_gvw,
    validate_string_length
)


class FuelType(str, Enum):
    DIESEL = "Diesel"
    BENZYNA = "Benzyna"
    LPG = "LPG"
    CNG = "CNG"
    HYBRYDA = "Hybryda"
    ELEKTRYCZNY = "Elektryczny"
    INNE = "Inne"


class GearboxType(str, Enum):
    MANUALNA = "Manualna"
    AUTOMATYCZNA = "Automatyczna"


class ConditionStatus(str, Enum):
    NOWY = "Nowy"
    UZYWANY = "Używany"
    USZKODZONY = "Uszkodzony"


class ListingBase(BaseModel):
    """Base model for listing with all common fields"""
    # SEKCJA 1: Informacje podstawowe
    title: str = Field(..., max_length=120, description="Tytuł ogłoszenia")
    price_pln: int = Field(..., ge=0, le=1_000_000, description="Cena w PLN")
    make: str = Field(..., max_length=60, description="Marka pojazdu")
    model: str = Field(..., max_length=60, description="Model pojazdu")
    color: Optional[str] = Field(None, max_length=40, description="Kolor")
    seats: Optional[int] = Field(None, ge=1, le=9, description="Liczba miejsc")
    production_year: int = Field(..., description="Rok produkcji")
    vin: Optional[str] = Field(None, max_length=17, description="Numer VIN")
    installments_available: bool = Field(False, description="Możliwość zakupu na raty")
    
    # SEKCJA 2: Specyfikacja techniczna
    fuel_type: FuelType = Field(..., description="Rodzaj paliwa")
    engine_displacement_cc: Optional[int] = Field(None, ge=100, le=10_000, description="Pojemność skokowa w cm³")
    power_hp: Optional[int] = Field(None, ge=20, le=2_000, description="Moc w KM")
    body_type: str = Field(..., max_length=40, description="Typ nadwozia")
    gearbox: GearboxType = Field(..., description="Skrzynia biegów")
    gvw_kg: Optional[int] = Field(None, ge=1_000, le=7_500, description="Dopuszczalna masa całkowita w kg")
    twin_rear_wheels: bool = Field(False, description="Podwójne tylne koła")
    
    # SEKCJA 3: Stan i historia pojazdu
    origin_country: Optional[str] = Field(None, max_length=60, description="Kraj pochodzenia")
    mileage_km: int = Field(..., ge=0, le=1_500_000, description="Przebieg w km")
    registration_number: Optional[str] = Field(None, max_length=15, description="Numer rejestracyjny")
    condition_status: ConditionStatus = Field(..., description="Stan pojazdu")
    first_registration_date: Optional[date] = Field(None, description="Data pierwszej rejestracji")
    accident_free: bool = Field(False, description="Bezwypadkowy")
    has_registration_number: bool = Field(False, description="Ma numer rejestracyjny")
    serviced_in_aso: bool = Field(False, description="Serwisowany w ASO")
    
    # SEKCJA 4: Opis sprzedawcy
    description_html: str = Field(..., min_length=20, max_length=10_000, description="Opis ogłoszenia (HTML)")
    home_delivery: bool = Field(False, description="Możliwość dostarczenia pod dom")
    tech_visual_short: Optional[str] = Field(None, max_length=280, description="Stan techniczny i wizualny (krótki opis)")
    seller_profile_url: Optional[str] = Field(None, max_length=200, description="Link do profilu sprzedawcy")
    location_street: Optional[str] = Field(None, max_length=120, description="Ulica/adres")
    location_city: str = Field(..., max_length=60, description="Miejscowość")
    location_region: str = Field(..., max_length=60, description="Województwo")
    
    # Additional fields from existing system
    zdjecia: List[str] = Field(default_factory=list, description="Lista URL zdjęć")
    zdjecieGlowne: Optional[str] = Field(None, description="URL głównego zdjęcia")
    wyrozniowane: bool = Field(False, description="Ogłoszenie wyróżnione")
    nowosc: bool = Field(False, description="Nowość")
    flotowy: bool = Field(False, description="Pojazd flotowy")
    gwarancja: bool = Field(False, description="Gwarancja")
    sold: bool = Field(False, description="Sprzedane")
    
    # Validators
    _validate_vin = validator('vin', allow_reuse=True)(validate_vin)
    _validate_production_year = validator('production_year', allow_reuse=True)(validate_production_year)
    _validate_first_registration_date = validator('first_registration_date', allow_reuse=True)(validate_first_registration_date)
    _validate_price = validator('price_pln', allow_reuse=True)(validate_price)
    _validate_mileage = validator('mileage_km', allow_reuse=True)(validate_mileage)
    _validate_seats = validator('seats', allow_reuse=True)(validate_seats)
    _validate_engine = validator('engine_displacement_cc', allow_reuse=True)(validate_engine_displacement)
    _validate_power = validator('power_hp', allow_reuse=True)(validate_power)
    _validate_gvw = validator('gvw_kg', allow_reuse=True)(validate_gvw)
    _validate_seller_url = validator('seller_profile_url', allow_reuse=True)(validate_url)
    _validate_registration = validator('registration_number', allow_reuse=True)(validate_registration_number)
    
    @validator('title')
    def validate_title(cls, v):
        return validate_string_length(v, "Tytuł", 120)
    
    @validator('color')
    def validate_color(cls, v):
        return validate_string_length(v, "Kolor", 40)
    
    @validator('origin_country')
    def validate_origin(cls, v):
        return validate_string_length(v, "Kraj pochodzenia", 60)
    
    @validator('tech_visual_short')
    def validate_tech_visual(cls, v):
        return validate_string_length(v, "Stan techniczny i wizualny", 280)
    
    @validator('location_street')
    def validate_street(cls, v):
        return validate_string_length(v, "Ulica", 120)


class ListingCreate(ListingBase):
    """Model for creating a new listing"""
    pass


class ListingUpdate(BaseModel):
    """Model for updating an existing listing - all fields optional"""
    # SEKCJA 1: Informacje podstawowe
    title: Optional[str] = Field(None, max_length=120)
    price_pln: Optional[int] = Field(None, ge=0, le=1_000_000)
    make: Optional[str] = Field(None, max_length=60)
    model: Optional[str] = Field(None, max_length=60)
    color: Optional[str] = Field(None, max_length=40)
    seats: Optional[int] = Field(None, ge=1, le=9)
    production_year: Optional[int] = None
    vin: Optional[str] = Field(None, max_length=17)
    installments_available: Optional[bool] = None
    
    # SEKCJA 2: Specyfikacja techniczna
    fuel_type: Optional[FuelType] = None
    engine_displacement_cc: Optional[int] = Field(None, ge=100, le=10_000)
    power_hp: Optional[int] = Field(None, ge=20, le=2_000)
    body_type: Optional[str] = Field(None, max_length=40)
    gearbox: Optional[GearboxType] = None
    gvw_kg: Optional[int] = Field(None, ge=1_000, le=7_500)
    twin_rear_wheels: Optional[bool] = None
    
    # SEKCJA 3: Stan i historia pojazdu
    origin_country: Optional[str] = Field(None, max_length=60)
    mileage_km: Optional[int] = Field(None, ge=0, le=1_500_000)
    registration_number: Optional[str] = Field(None, max_length=15)
    condition_status: Optional[ConditionStatus] = None
    first_registration_date: Optional[date] = None
    accident_free: Optional[bool] = None
    has_registration_number: Optional[bool] = None
    serviced_in_aso: Optional[bool] = None
    
    # SEKCJA 4: Opis sprzedawcy
    description_html: Optional[str] = Field(None, min_length=20, max_length=10_000)
    home_delivery: Optional[bool] = None
    tech_visual_short: Optional[str] = Field(None, max_length=280)
    seller_profile_url: Optional[str] = Field(None, max_length=200)
    location_street: Optional[str] = Field(None, max_length=120)
    location_city: Optional[str] = Field(None, max_length=60)
    location_region: Optional[str] = Field(None, max_length=60)
    
    # Additional fields
    zdjecia: Optional[List[str]] = None
    zdjecieGlowne: Optional[str] = None
    wyrozniowane: Optional[bool] = None
    nowosc: Optional[bool] = None
    flotowy: Optional[bool] = None
    gwarancja: Optional[bool] = None
    sold: Optional[bool] = None
    
    # Validators - same as base
    _validate_vin = validator('vin', allow_reuse=True)(validate_vin)
    _validate_production_year = validator('production_year', allow_reuse=True)(validate_production_year)
    _validate_first_registration_date = validator('first_registration_date', allow_reuse=True)(validate_first_registration_date)
    _validate_price = validator('price_pln', allow_reuse=True)(validate_price)
    _validate_mileage = validator('mileage_km', allow_reuse=True)(validate_mileage)
    _validate_seats = validator('seats', allow_reuse=True)(validate_seats)
    _validate_engine = validator('engine_displacement_cc', allow_reuse=True)(validate_engine_displacement)
    _validate_power = validator('power_hp', allow_reuse=True)(validate_power)
    _validate_gvw = validator('gvw_kg', allow_reuse=True)(validate_gvw)
    _validate_seller_url = validator('seller_profile_url', allow_reuse=True)(validate_url)
    _validate_registration = validator('registration_number', allow_reuse=True)(validate_registration_number)


class Listing(ListingBase):
    """Full listing model with system fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
