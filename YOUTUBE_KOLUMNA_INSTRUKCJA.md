# WAŻNE: Dodaj kolumnę YouTube URL do bazy danych

## Problem
Link YouTube nie zapisuje się, ponieważ kolumna nie istnieje w bazie Supabase.

## Rozwiązanie
Musisz wykonać ten SQL w Supabase SQL Editor:

```sql
-- Dodaj kolumnę youtubeUrl do tabeli buses
ALTER TABLE buses ADD COLUMN IF NOT EXISTS "youtubeUrl" TEXT;

-- Dodaj komentarz dla dokumentacji
COMMENT ON COLUMN buses."youtubeUrl" IS 'URL do filmiku YouTube dla ogłoszenia';
```

## Jak to zrobić:

1. Zaloguj się do Supabase Dashboard: https://supabase.com/dashboard
2. Wybierz swój projekt
3. Kliknij **"SQL Editor"** w lewym menu
4. Kliknij **"New query"**
5. Wklej powyższy kod SQL
6. Kliknij **"Run"** (lub naciśnij Ctrl+Enter)
7. Zobaczysz: "Success. No rows returned" ✅

## Po wykonaniu SQL:

1. Odśwież stronę z panelem admina (F5)
2. Edytuj dowolne ogłoszenie
3. Wklej link YouTube w pole "Link do filmiku YouTube"
4. Zapisz
5. Filmik pojawi się na stronie ogłoszenia! 🎥

## Uwaga:
To jest jednorazowa operacja. Po dodaniu kolumny wszystko będzie działać automatycznie dla wszystkich ogłoszeń (nowych i edytowanych).
