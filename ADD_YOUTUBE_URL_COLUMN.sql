-- Dodaj kolumnę youtubeUrl do tabeli buses
ALTER TABLE buses ADD COLUMN IF NOT EXISTS "youtubeUrl" TEXT;

-- Dodaj komentarz dla dokumentacji
COMMENT ON COLUMN buses."youtubeUrl" IS 'URL do filmiku YouTube dla ogłoszenia';
