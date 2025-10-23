# 🚀 PRZEBUDOWA FORMULARZA OGŁOSZEŃ - INSTRUKCJA WDROŻENIA

## ✅ Co zostało zrobione

### Backend (100%)
- ✅ SQL migracja z nowymi kolumnami (`SUPABASE_MIGRATION_LISTINGS.sql`)
- ✅ Walidatory dla wszystkich pól (VIN, URL, daty, zakresy) w `validators.py`
- ✅ Nowe modele Pydantic w `listing_models.py` z pełnymi walidacjami
- ✅ Endpointy API: `POST/PUT/GET /api/admin/listings`
- ✅ 45 testów jednostkowych (wszystkie przechodzą) w `tests/test_validators.py`

### Frontend (100%)
- ✅ Nowy komponent `BusFormNew.jsx` z 4 sekcjami
- ✅ Integracja z React Quill (rich text editor)
- ✅ Integracja z React DatePicker (pl locale)
- ✅ Walidacje inline w języku polskim
- ✅ Import z Otomoto (zachowany i ulepszony)
- ✅ Formatowanie liczb (tysiące z spacją)
- ✅ Nowe metody API w `busApi.js`

## 📋 KROK 1: Migracja bazy danych (WYMAGANE!)

**WAŻNE:** Musisz wykonać migrację SQL w Supabase przed użyciem nowego formularza!

1. Zaloguj się do [Supabase Dashboard](https://supabase.com)
2. Wybierz swój projekt
3. Przejdź do **SQL Editor**
4. Otwórz plik `/app/SUPABASE_MIGRATION_LISTINGS.sql`
5. Skopiuj całą zawartość
6. Wklej do SQL Editor i kliknij **Run**

### Co robi migracja:
- Dodaje nowe kolumny do tabeli `buses`:
  - `title` - tytuł ogłoszenia
  - `color` - kolor pojazdu
  - `vin` - numer VIN
  - `installments_available` - możliwość rat
  - `gvw_kg` - dopuszczalna masa całkowita
  - `twin_rear_wheels` - podwójne tylne koła
  - `origin_country` - kraj pochodzenia
  - `registration_number` - numer rejestracyjny
  - `condition_status` - stan pojazdu
  - `first_registration_date` - data pierwszej rejestracji
  - `accident_free` - bezwypadkowy
  - `has_registration_number` - ma numer rej.
  - `serviced_in_aso` - serwisowany w ASO
  - `description_html` - opis HTML
  - `home_delivery` - dostawa pod dom
  - `tech_visual_short` - krótki opis stanu
  - `seller_profile_url` - link do profilu
  - `location_street`, `location_city`, `location_region` - lokalizacja
- Tworzy indeksy dla wydajności
- Ustawia wartości domyślne dla istniejących rekordów

**Status migracji:** ⏳ Do wykonania przez użytkownika

## 🎯 KROK 2: Restart aplikacji

Po wykonaniu migracji SQL, aplikacja jest gotowa do użycia!

Backend i frontend zostały już zaktualizowane i uruchomione.

## 📝 STRUKTURA NOWEGO FORMULARZA

### Sekcja 1: Informacje podstawowe
- Tytuł ogłoszenia* (max 120 znaków)
- Cena w PLN* (0-1,000,000)
- Marka* i Model*
- Kolor, Liczba miejsc (1-9)
- Rok produkcji* (1950-2025)
- Numer VIN (17 znaków, bez I/O/Q)
- Możliwość zakupu na raty (checkbox)

### Sekcja 2: Specyfikacja techniczna
- Rodzaj paliwa* (Diesel, Benzyna, LPG, CNG, Hybryda, Elektryczny)
- Pojemność skokowa (100-10,000 cm³)
- Moc (20-2,000 KM)
- Typ nadwozia* (Furgon blaszak/wysoki, Skrzyniowy, Kontener, Mixto)
- Skrzynia biegów* (Manualna/Automatyczna)
- DMC (1,000-7,500 kg)
- Podwójne tylne koła (checkbox)

### Sekcja 3: Stan i historia pojazdu
- Przebieg w km* (0-1,500,000)
- Stan pojazdu* (Nowy/Używany/Uszkodzony)
- Kraj pochodzenia
- Data pierwszej rejestracji (date picker PL)
- Numer rejestracyjny (regex: A-Z0-9 \- spacja)
- Bezwypadkowy, Ma numer rej., Serwisowany w ASO (checkboxes)

### Sekcja 4: Opis sprzedawcy
- Opis ogłoszenia* (rich text, 20-10,000 znaków)
- Stan techniczny i wizualny (max 280 znaków)
- Link do profilu sprzedawcy (walidacja URL)
- Lokalizacja: Ulica, Miejscowość*, Województwo*
- Możliwość dostarczenia pod dom (checkbox)
- Zdjęcia (upload + zarządzanie)
- Dodatkowe opcje: Wyróżnione, Nowość, Flotowy, Gwarancja

**Pola wymagane oznaczone gwiazdką (*)**

## 🧪 TESTY

### Uruchom testy walidatorów:
```bash
cd /app/backend
python -m pytest tests/test_validators.py -v
```

**Wynik:** ✅ 45/45 testów przechodzi

### Przykładowe testy:
- ✅ VIN validation (17 znaków, bez I/O/Q)
- ✅ URL validation (http/https)
- ✅ Registration number (3-15 znaków)
- ✅ Production year (1950-2025)
- ✅ Date validation (nie w przyszłości)
- ✅ Price range (0-1,000,000)
- ✅ Mileage range (0-1,500,000)
- ✅ Seats (1-9)
- ✅ Engine displacement (100-10,000)
- ✅ Power (20-2,000)
- ✅ GVW (1,000-7,500)

## 🔧 USAGE

### Dodawanie nowego ogłoszenia:
1. Przejdź do Panelu Admina
2. Kliknij "Dodaj ogłoszenie"
3. (Opcjonalnie) Wklej URL z Otomoto i kliknij "Importuj dane"
4. Wypełnij formularz sekcja po sekcji
5. Kliknij "Dodaj ogłoszenie" w sekcji 4

### Edycja istniejącego ogłoszenia:
1. W Panelu Admina kliknij "Edytuj" przy ogłoszeniu
2. Wprowadź zmiany
3. Kliknij "Zapisz zmiany"

## 🔌 API ENDPOINTS

### Nowe endpointy:
```
POST   /api/admin/listings     - Tworzenie ogłoszenia
PUT    /api/admin/listings/:id - Edycja ogłoszenia
GET    /api/admin/listings/:id - Pobieranie ogłoszenia
```

### Przykładowy request (POST):
```json
{
  "title": "Renault Master L3H2 2.3 dCi 163 KM, blaszak",
  "price_pln": 52900,
  "make": "Renault",
  "model": "Master",
  "production_year": 2016,
  "fuel_type": "Diesel",
  "gearbox": "Manualna",
  "body_type": "Furgon (blaszak)",
  "mileage_km": 222000,
  "condition_status": "Używany",
  "description_html": "<p>Auto w bardzo dobrym stanie...</p>",
  "location_city": "Smyków",
  "location_region": "Świętokrzyskie"
}
```

### Błędy walidacji (422):
```json
{
  "detail": {
    "errors": {
      "vin": "VIN musi mieć dokładnie 17 znaków",
      "price_pln": "Cena nie może być ujemna"
    },
    "message": "Błędy walidacji"
  }
}
```

## 📚 PLIKI UTWORZONE/ZMODYFIKOWANE

### Backend:
- ✅ `/app/backend/validators.py` - Walidatory dla wszystkich pól
- ✅ `/app/backend/listing_models.py` - Nowe modele Pydantic
- ✅ `/app/backend/tests/test_validators.py` - 45 testów jednostkowych
- ✅ `/app/backend/server.py` - Dodane endpointy `/api/admin/listings`
- ✅ `/app/SUPABASE_MIGRATION_LISTINGS.sql` - SQL migracja

### Frontend:
- ✅ `/app/frontend/src/components/BusFormNew.jsx` - Nowy formularz 4-sekcyjny
- ✅ `/app/frontend/src/api/busApi.js` - Nowe metody API
- ✅ `/app/frontend/src/pages/AdminPanel.jsx` - Użycie nowego formularza
- ✅ `/app/frontend/package.json` - Dodane: react-quill, react-datepicker

## ⚠️ WAŻNE UWAGI

1. **Kompatybilność wsteczna:** Stare ogłoszenia działają nadal! Nowy system mapuje stare pola na nowe.
2. **Otomoto scraper:** Zachowany i ulepszony - teraz importuje wszystkie nowe pola.
3. **Walidacje:** Wszystkie walidacje działają zarówno na frontendzie (instant feedback) jak i backendzie (security).
4. **Data picker:** Używa polskiej lokalizacji (pl-PL), akceptuje DD.MM.RRRR i RRRR-MM-DD.
5. **Rich text:** Quill editor z podstawowymi funkcjami (pogrubienie, listy, linki).

## 🎉 GOTOWE!

Po wykonaniu migracji SQL (KROK 1), możesz:
- ✅ Dodawać nowe ogłoszenia z rozszerzonymi polami
- ✅ Edytować istniejące ogłoszenia
- ✅ Importować dane z Otomoto
- ✅ Korzystać z walidacji inline
- ✅ Używać rich text editora do opisów

## 📞 WSPARCIE

W razie problemów:
1. Sprawdź logi backendu: `tail -f /var/log/supervisor/backend.err.log`
2. Sprawdź konsolę przeglądarki (F12)
3. Uruchom testy: `pytest backend/tests/test_validators.py -v`

---

**Status:** ✅ Backend 100% | ✅ Frontend 100% | ⏳ Migracja SQL (do wykonania)
