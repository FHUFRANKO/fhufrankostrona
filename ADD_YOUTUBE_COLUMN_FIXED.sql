-- Dodaj kolumnę youtube_url (snake_case) do tabeli buses
ALTER TABLE buses ADD COLUMN IF NOT EXISTS youtube_url TEXT;

-- Dodaj komentarz
COMMENT ON COLUMN buses.youtube_url IS 'URL do filmiku YouTube dla ogłoszenia';

-- Odśwież schema cache
NOTIFY pgrst, 'reload schema';
