# ⚠️ WYKONAJ TO NATYCHMIAST! ⚠️

## Problem:
Błąd: `Could not find the 'accident_free' column of 'buses' in the schema cache`

**Oznacza to:** NIE wykonałeś głównej migracji SQL!

---

## ROZWIĄZANIE (3 minuty):

### KROK 1: Otwórz Supabase SQL Editor
1. Wejdź na: https://supabase.com
2. Zaloguj się
3. Wybierz swój projekt (fhufranko)
4. W menu po lewej kliknij **"SQL Editor"** (ikona </>)

### KROK 2: Skopiuj poniższy SQL
**SKOPIUJ CAŁOŚĆ (od linii 1 do końca):**

```sql
-- MIGRACJA: Rozszerzenie tabeli buses o nowe pola dla systemu ogłoszeń
-- Data: 2025-10-23
-- Wykonaj w Supabase SQL Editor

-- ========================================
-- SEKCJA 1: Informacje podstawowe
-- ========================================

-- title (zmiana z marka+model będzie w kodzie aplikacji, tu dodajemy kolumnę)
ALTER TABLE buses ADD COLUMN IF NOT EXISTS title VARCHAR(120);

-- color
ALTER TABLE buses ADD COLUMN IF NOT EXISTS color VARCHAR(40);

-- vin
ALTER TABLE buses ADD COLUMN IF NOT EXISTS vin CHAR(17);

-- installments_available
ALTER TABLE buses ADD COLUMN IF NOT EXISTS installments_available BOOLEAN NOT NULL DEFAULT false;

-- ========================================
-- SEKCJA 2: Specyfikacja techniczna
-- ========================================

-- gvw_kg (dopuszczalna masa całkowita)
ALTER TABLE buses ADD COLUMN IF NOT EXISTS gvw_kg INTEGER;

-- twin_rear_wheels
ALTER TABLE buses ADD COLUMN IF NOT EXISTS twin_rear_wheels BOOLEAN NOT NULL DEFAULT false;

-- ========================================
-- SEKCJA 3: Stan i historia pojazdu
-- ========================================

-- origin_country
ALTER TABLE buses ADD COLUMN IF NOT EXISTS origin_country VARCHAR(60);

-- registration_number
ALTER TABLE buses ADD COLUMN IF NOT EXISTS registration_number VARCHAR(15);

-- condition_status
ALTER TABLE buses ADD COLUMN IF NOT EXISTS condition_status VARCHAR(12);

-- first_registration_date
ALTER TABLE buses ADD COLUMN IF NOT EXISTS first_registration_date DATE;

-- accident_free
ALTER TABLE buses ADD COLUMN IF NOT EXISTS accident_free BOOLEAN NOT NULL DEFAULT false;

-- has_registration_number
ALTER TABLE buses ADD COLUMN IF NOT EXISTS has_registration_number BOOLEAN NOT NULL DEFAULT false;

-- serviced_in_aso
ALTER TABLE buses ADD COLUMN IF NOT EXISTS serviced_in_aso BOOLEAN NOT NULL DEFAULT false;

-- ========================================
-- SEKCJA 4: Opis sprzedawcy
-- ========================================

-- description_html (używamy istniejące pole opis, zmienimy typ)
ALTER TABLE buses ALTER COLUMN opis TYPE TEXT;
ALTER TABLE buses ADD COLUMN IF NOT EXISTS description_html TEXT;

-- home_delivery
ALTER TABLE buses ADD COLUMN IF NOT EXISTS home_delivery BOOLEAN NOT NULL DEFAULT false;

-- tech_visual_short
ALTER TABLE buses ADD COLUMN IF NOT EXISTS tech_visual_short VARCHAR(280);

-- seller_profile_url
ALTER TABLE buses ADD COLUMN IF NOT EXISTS seller_profile_url VARCHAR(200);

-- location_street
ALTER TABLE buses ADD COLUMN IF NOT EXISTS location_street VARCHAR(120);

-- location_city
ALTER TABLE buses ADD COLUMN IF NOT EXISTS location_city VARCHAR(60);

-- location_region
ALTER TABLE buses ADD COLUMN IF NOT EXISTS location_region VARCHAR(60);

-- ========================================
-- INDEKSY dla wydajności
-- ========================================

CREATE INDEX IF NOT EXISTS idx_buses_vin ON buses(vin) WHERE vin IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_buses_price ON buses("cenaBrutto");
CREATE INDEX IF NOT EXISTS idx_buses_condition_status ON buses(condition_status);
CREATE INDEX IF NOT EXISTS idx_buses_origin_country ON buses(origin_country);
CREATE INDEX IF NOT EXISTS idx_buses_title ON buses(title);

-- ========================================
-- Ustaw wartości domyślne dla istniejących rekordów
-- ========================================

UPDATE buses SET condition_status = 'Używany' WHERE condition_status IS NULL;
UPDATE buses SET location_city = 'Smyków' WHERE location_city IS NULL;
UPDATE buses SET location_region = 'Świętokrzyskie' WHERE location_region IS NULL;
```

### KROK 3: Wykonaj w Supabase
1. Wklej skopiowany SQL do SQL Editor
2. Kliknij **"RUN"** (zielony przycisk)
3. Poczekaj 5 sekund
4. Powinieneś zobaczyć: **"Success. No rows returned"**

### KROK 4: Sprawdź czy działa
1. Odśwież stronę fhufranko.com/admin
2. Kliknij "Dodaj ogłoszenie"
3. Wypełnij formularz
4. Kliknij "Dodaj ogłoszenie"
5. **POWINNO DZIAŁAĆ!** ✅

---

## ✅ Co robi ta migracja?

Dodaje **26 nowych kolumn** do tabeli `buses`:
- `title` - tytuł ogłoszenia
- `color` - kolor pojazdu
- `vin` - numer VIN
- `installments_available` - raty
- `gvw_kg` - DMC
- `twin_rear_wheels` - podwójne koła
- `origin_country` - kraj pochodzenia
- `registration_number` - numer rejestracyjny
- `condition_status` - stan (Nowy/Używany/Uszkodzony)
- `first_registration_date` - data pierwszej rejestracji
- `accident_free` - bezwypadkowy
- `has_registration_number` - ma numer rej.
- `serviced_in_aso` - serwisowany w ASO
- `description_html` - opis HTML
- `home_delivery` - dostawa pod dom
- `tech_visual_short` - stan techniczny (krótko)
- `seller_profile_url` - profil sprzedawcy
- `location_street` - ulica
- `location_city` - miejscowość
- `location_region` - województwo

Plus indeksy dla wydajności.

---

## ❓ Pytania?

Jeśli coś nie działa:
1. Sprawdź czy w Supabase pokazało "Success"
2. Sprawdź logi Railway (czy backend się zrestartował)
3. Odśwież przeglądarkę (Ctrl+F5)

**Po wykonaniu tej migracji wszystko powinno działać!**
