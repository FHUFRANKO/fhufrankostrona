-- Dodaj nowe kolumny do tabeli buses w Supabase
-- Wykonaj to w SQL Editor w Supabase Dashboard

ALTER TABLE buses 
ADD COLUMN IF NOT EXISTS kolor TEXT,
ADD COLUMN IF NOT EXISTS "krajPochodzenia" TEXT,
ADD COLUMN IF NOT EXISTS stan TEXT,
ADD COLUMN IF NOT EXISTS bezwypadkowy BOOLEAN;

-- Ustaw wartości domyślne dla istniejących rekordów
UPDATE buses SET stan = 'Używany' WHERE stan IS NULL;
