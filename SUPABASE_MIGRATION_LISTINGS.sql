-- MIGRACJA: Rozszerzenie tabeli buses o nowe pola dla systemu ogłoszeń
-- Data: 2025-10-23
-- Wykonaj w Supabase SQL Editor

-- ========================================
-- SEKCJA 1: Informacje podstawowe
-- ========================================

-- title (zmiana z marka+model będzie w kodzie aplikacji, tu dodajemy kolumnę)
ALTER TABLE buses ADD COLUMN IF NOT EXISTS title VARCHAR(120);

-- price_pln (używamy cenaBrutto jako price_pln)
-- Już istnieje jako cenaBrutto, dodamy alias w aplikacji

-- make, model (już istnieją jako marka, model)
-- color
ALTER TABLE buses ADD COLUMN IF NOT EXISTS color VARCHAR(40);

-- seats (już istnieje jako liczbaMiejsc)
-- production_year (już istnieje jako rok)

-- vin
ALTER TABLE buses ADD COLUMN IF NOT EXISTS vin CHAR(17);

-- installments_available
ALTER TABLE buses ADD COLUMN IF NOT EXISTS installments_available BOOLEAN NOT NULL DEFAULT false;

-- ========================================
-- SEKCJA 2: Specyfikacja techniczna
-- ========================================

-- fuel_type (już istnieje jako paliwo)
-- engine_displacement_cc (już istnieje jako kubatura)
-- power_hp (już istnieje jako moc)
-- body_type (już istnieje jako typNadwozia)
-- gearbox (już istnieje jako skrzynia)

-- gvw_kg (dopuszczalna masa całkowita)
ALTER TABLE buses ADD COLUMN IF NOT EXISTS gvw_kg INTEGER;

-- twin_rear_wheels
ALTER TABLE buses ADD COLUMN IF NOT EXISTS twin_rear_wheels BOOLEAN NOT NULL DEFAULT false;

-- ========================================
-- SEKCJA 3: Stan i historia pojazdu
-- ========================================

-- origin_country
ALTER TABLE buses ADD COLUMN IF NOT EXISTS origin_country VARCHAR(60);

-- mileage_km (już istnieje jako przebieg)

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

-- created_at (już istnieje)

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

-- ========================================
-- UWAGA: Po wykonaniu migracji należy:
-- 1. Zrestartować backend
-- 2. Przetestować dodawanie/edycję ogłoszeń
-- 3. Sprawdzić czy wszystkie pola są poprawnie zapisywane
-- ========================================
