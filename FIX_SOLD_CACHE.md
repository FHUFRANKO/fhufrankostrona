# 🔄 ODŚWIEŻENIE CACHE SUPABASE

## Problem:
Checkbox "SPRZEDANE" zapisuje się (200 OK), ale overlay nie pojawia się na froncie.

## Rozwiązanie:

### KROK 1: Odśwież cache schema w Supabase

W Supabase Dashboard wykonaj:

```sql
-- Odśwież cache schema
NOTIFY pgrst, 'reload schema';
```

### KROK 2: Alternatywnie - restart PostgREST

Jeśli powyższe nie działa:

1. Wejdź w **Supabase Dashboard**
2. **Project Settings** → **API**
3. Kliknij **"Restart PostgREST"** lub **"Reload Schema"**

### KROK 3: Wyczyść cache przeglądarki

1. Odśwież stronę z **Ctrl+Shift+R** (hard refresh)
2. Lub wyczyść cache przeglądarki

### KROK 4: Test

1. Wejdź na stronę z ogłoszeniami: fhufranko.com/ogloszenia
2. Ogłoszenie ze zaznaczonym "SPRZEDANE" powinno mieć czerwony overlay
3. Jeśli nie ma - sprawdź konsolę przeglądarki (F12)

---

## Szybki test - sprawdź czy pole `sold` jest zwracane:

Otwórz konsolę przeglądarki (F12) i wpisz:

```javascript
fetch('https://fhufranko.com/api/ogloszenia')
  .then(r => r.json())
  .then(data => console.log(data[0]))
```

Sprawdź czy w obiekcie jest pole `sold: true` lub `sold: false`.

Jeśli NIE MA pola `sold` - to znaczy że Supabase cache nie został odświeżony.

---

## Jeśli nadal nie działa:

Wyślij mi wynik powyższego testu z konsoli.
