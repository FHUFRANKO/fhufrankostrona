"""
Validators for bus listing fields
"""
import re
from datetime import datetime, date
from typing import Optional
from pydantic import validator, Field
from urllib.parse import urlparse


def validate_vin(v: Optional[str]) -> Optional[str]:
    """
    Validate VIN number:
    - Must be exactly 17 characters
    - Only A-Z (uppercase) and 0-9 allowed
    - Letters I, O, Q are NOT allowed
    """
    if v is None or v == "":
        return None
    
    v = v.strip().upper()
    
    if len(v) != 17:
        raise ValueError(f"VIN musi mieć dokładnie 17 znaków (podano: {len(v)})")
    
    vin_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
    if not re.match(vin_pattern, v):
        raise ValueError("VIN może zawierać tylko wielkie litery A-Z (bez I, O, Q) i cyfry 0-9")
    
    return v


def validate_url(v: Optional[str]) -> Optional[str]:
    """
    Validate URL format
    """
    if v is None or v == "":
        return None
    
    v = v.strip()
    
    try:
        result = urlparse(v)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Nieprawidłowy format URL. URL musi zawierać protokół (http/https) i domenę")
        
        if result.scheme not in ['http', 'https']:
            raise ValueError("URL musi zaczynać się od http:// lub https://")
            
        return v
    except Exception as e:
        raise ValueError(f"Nieprawidłowy URL: {str(e)}")


def validate_registration_number(v: Optional[str]) -> Optional[str]:
    """
    Validate Polish registration number format
    - 3-15 characters
    - Uppercase letters, digits, spaces, hyphens only
    """
    if v is None or v == "":
        return None
    
    v = v.strip().upper()
    
    if len(v) < 3 or len(v) > 15:
        raise ValueError(f"Numer rejestracyjny musi mieć od 3 do 15 znaków (podano: {len(v)})")
    
    reg_pattern = r'^[A-Z0-9\- ]{3,15}$'
    if not re.match(reg_pattern, v):
        raise ValueError("Numer rejestracyjny może zawierać tylko wielkie litery, cyfry, spacje i myślniki")
    
    return v


def validate_production_year(v: int) -> int:
    """
    Validate production year:
    - Must be between 1950 and current year
    """
    current_year = datetime.now().year
    
    if v < 1950:
        raise ValueError("Rok produkcji nie może być wcześniejszy niż 1950")
    
    if v > current_year:
        raise ValueError(f"Rok produkcji nie może być późniejszy niż {current_year}")
    
    return v


def validate_first_registration_date(v: Optional[date]) -> Optional[date]:
    """
    Validate first registration date:
    - Cannot be in the future
    - Cannot be before 1950-01-01
    """
    if v is None:
        return None
    
    min_date = date(1950, 1, 1)
    today = date.today()
    
    if v < min_date:
        raise ValueError(f"Data pierwszej rejestracji nie może być wcześniejsza niż {min_date}")
    
    if v > today:
        raise ValueError("Data pierwszej rejestracji nie może być w przyszłości")
    
    return v


def validate_price(v: int) -> int:
    """
    Validate price:
    - Must be >= 0
    - Must be <= 1,000,000
    """
    if v < 0:
        raise ValueError("Cena nie może być ujemna")
    
    if v > 1_000_000:
        raise ValueError("Cena nie może przekraczać 1,000,000 PLN")
    
    return v


def validate_mileage(v: int) -> int:
    """
    Validate mileage:
    - Must be >= 0
    - Must be <= 1,500,000 km
    """
    if v < 0:
        raise ValueError("Przebieg nie może być ujemny")
    
    if v > 1_500_000:
        raise ValueError("Przebieg nie może przekraczać 1,500,000 km")
    
    return v


def validate_seats(v: Optional[int]) -> Optional[int]:
    """
    Validate number of seats:
    - Must be between 1 and 9
    """
    if v is None:
        return None
    
    if v < 1:
        raise ValueError("Liczba miejsc musi być co najmniej 1")
    
    if v > 9:
        raise ValueError("Liczba miejsc nie może przekraczać 9")
    
    return v


def validate_engine_displacement(v: Optional[int]) -> Optional[int]:
    """
    Validate engine displacement:
    - Must be between 100 and 10,000 cc
    """
    if v is None:
        return None
    
    if v < 100:
        raise ValueError("Pojemność skokowa nie może być mniejsza niż 100 cm³")
    
    if v > 10_000:
        raise ValueError("Pojemność skokowa nie może przekraczać 10,000 cm³")
    
    return v


def validate_power(v: Optional[int]) -> Optional[int]:
    """
    Validate engine power:
    - Must be between 20 and 2,000 HP
    """
    if v is None:
        return None
    
    if v < 20:
        raise ValueError("Moc nie może być mniejsza niż 20 KM")
    
    if v > 2_000:
        raise ValueError("Moc nie może przekraczać 2,000 KM")
    
    return v


def validate_gvw(v: Optional[int]) -> Optional[int]:
    """
    Validate gross vehicle weight:
    - Must be between 1,000 and 7,500 kg
    """
    if v is None:
        return None
    
    if v < 1_000:
        raise ValueError("Dopuszczalna masa całkowita nie może być mniejsza niż 1,000 kg")
    
    if v > 7_500:
        raise ValueError("Dopuszczalna masa całkowita nie może przekraczać 7,500 kg")
    
    return v


def validate_string_length(v: Optional[str], field_name: str, max_length: int) -> Optional[str]:
    """
    Generic string length validator
    """
    if v is None or v == "":
        return None
    
    v = v.strip()
    
    if len(v) > max_length:
        raise ValueError(f"{field_name} nie może przekraczać {max_length} znaków (podano: {len(v)})")
    
    return v
