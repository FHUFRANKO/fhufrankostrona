# Panel Admina - FHU FRANKO

System autoryzacji z **dwuwarstwową ochroną**:
1. **Ukryty URL + hasło** - podstawowa ochrona przed nieautoryzowanym dostępem
2. **Supabase JWT** - zaawansowana autoryzacja API dla adminów

## 🔐 Ukryty URL + Hasło (Warstwa 1)

Panel admina jest chroniony przez:
- **Ukryty URL**: `/admin-{ADMIN_PATH}` zamiast publicznego `/admin`
- **Hasło dostępu**: prosty formularz z hasłem
- **Cookie sesyjny**: HMAC-podpisane cookie ważne 8h

### Konfiguracja ukrytego dostępu

W pliku `/app/backend/.env` ustaw:

```env
# Zmień na unikalną, losową wartość (np. uuid bez kresek)
ADMIN_PATH="moj-tajny-panel-82374"

# Silne hasło dostępu do panelu
ADMIN_PASSWORD="ZmienMnieTeraz123!"

# Sekret do podpisywania cookies (min. 32 znaki)
ADMIN_COOKIE_SECRET="ZmienTenSekret123!"
```

**WAŻNE:**
- `ADMIN_PATH` - zmień na unikalną wartość (np. `a8f3k2m9p1x7q5w4`)
- `ADMIN_PASSWORD` - użyj silnego hasła (min. 12 znaków)
- `ADMIN_COOKIE_SECRET` - wygeneruj losowy ciąg (min. 32 znaki)

### Jak działa ochrona?

1. Użytkownik klika "Panel Admina" na stronie → przekierowanie na `/admin-{ADMIN_PATH}`
2. Wyświetla się formularz z hasłem
3. Po wpisaniu poprawnego hasła → ustawiane jest cookie i przekierowanie na `/admin`
4. Wszystkie `/admin/*` są chronione middleware - bez cookie → redirect na login
5. Cookie ważne 8h, potem trzeba się zalogować ponownie

### Test ochrony

```bash
# Próba dostępu bez cookie → 303 redirect
curl -i http://localhost:8001/admin

# Ukryta strona logowania
curl http://localhost:8001/admin-moj-tajny-panel-82374
```

---

## 📋 Spis treści

1. [Wymagania](#wymagania)
2. [Konfiguracja Supabase](#konfiguracja-supabase)
3. [Konfiguracja backendu](#konfiguracja-backendu)
4. [Konfiguracja frontendu](#konfiguracja-frontendu)
5. [Uruchomienie](#uruchomienie)
6. [Testowanie](#testowanie)
7. [Struktura projektu](#struktura-projektu)

## Wymagania

- Python 3.9+
- Node.js 16+
- MongoDB
- Konto Supabase (darmowy tier wystarczy)

## Konfiguracja Supabase

### 1. Utwórz projekt w Supabase

Przejdź do [https://app.supabase.com](https://app.supabase.com) i utwórz nowy projekt.

### 2. Dodaj użytkowników administratorów

W panelu Supabase:
1. Przejdź do **Authentication** → **Users**
2. Kliknij **Add user** → **Create new user**
3. Wprowadź email i hasło
4. Zapisz adres email - będzie potrzebny w konfiguracji `ADMIN_EMAILS`

### 3. Pobierz klucze API

W panelu Supabase przejdź do **Settings** → **API**:

- **URL**: Skopiuj `Project URL` (np. `https://xxxxx.supabase.co`)
- **ANON KEY**: Skopiuj `anon` `public` key
- **JWT SECRET**: Skopiuj `JWT Secret` (w sekcji **JWT Settings**)

## Konfiguracja backendu

### 1. Uzupełnij plik `.env`

W katalogu `/app/backend/.env` uzupełnij następujące wartości:

```env
# Supabase Configuration
SUPABASE_URL="https://xxxxx.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_JWT_SECRET="twoj-jwt-secret-z-supabase"

# Admin Configuration
ADMIN_EMAILS="admin@example.com,admin2@example.com"

# API Configuration
API_BASE_URL="https://twoja-domena.com"
```

**WAŻNE:** 
- `ADMIN_EMAILS` - lista emaili rozdzielona przecinkami (bez spacji)
- Tylko użytkownicy z tych emaili będą mieli dostęp do panelu admina

### 2. Zainstaluj zależności

```bash
cd /app/backend
pip install -r requirements.txt
```

### 3. Restart backendu

```bash
sudo supervisorctl restart backend
```

## Konfiguracja frontendu

### 1. Uzupełnij plik `env.js`

W katalogu `/app/frontend/public/env.js` (lub skopiuj z `env.js.template`):

```javascript
window.ENV = window.ENV || {};
Object.assign(window.ENV, {
  SUPABASE_URL: "https://xxxxx.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  API_BASE_URL: "https://twoja-domena.com"
});
```

### 2. Zainstaluj zależności i uruchom

```bash
cd /app/frontend
yarn install
yarn start
```

## Uruchomienie

### Opcja 1: Development (lokalnie)

**Backend:**
```bash
cd /app/backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```bash
cd /app/frontend
yarn start
```

**Dostęp:**
- Panel admina: http://localhost:3000/admin.html
- API: http://localhost:8001/api/

### Opcja 2: Production (Supervisor)

```bash
sudo supervisorctl restart all
sudo supervisorctl status
```

**Dostęp:**
- Panel admina: https://twoja-domena.com/admin
- API: https://twoja-domena.com/api/

## Testowanie

### Test 1: Endpoint /me bez tokenu (oczekiwany wynik: 401)

```bash
curl -i http://localhost:8001/api/me
```

**Oczekiwany wynik:**
```
HTTP/1.1 401 Unauthorized
{"detail":"Authorization header missing"}
```

### Test 2: Logowanie w panelu admina

1. Otwórz http://localhost:3000/admin.html (lub /admin na produkcji)
2. Wprowadź email i hasło użytkownika z Supabase
3. Kliknij "Zaloguj się"

**Przypadek A - Email NIE jest w ADMIN_EMAILS:**
```
"Brak uprawnień administratora dla: user@example.com"
```

**Przypadek B - Email JEST w ADMIN_EMAILS:**
- Panel się otworzy
- Zobaczysz status: "Zalogowano jako: admin@example.com [ADMIN]"
- Możesz testować endpointy API

### Test 3: Dostęp do zabezpieczonych endpointów

**Bez tokenu (401):**
```bash
curl -i http://localhost:8001/api/opinie
```

**Z tokenem użytkownika spoza listy adminów (403):**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/opinie
```

**Z tokenem admina (200):**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/opinie
```

### Test 4: Endpoint /me z tokenem admina

```bash
TOKEN="twoj-token-z-supabase"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/me
```

**Oczekiwany wynik (admin):**
```json
{
  "email": "admin@example.com",
  "admin": true,
  "user_id": "uuid-user-id",
  "authenticated": true
}
```

**Oczekiwany wynik (nie-admin):**
```json
{
  "email": "user@example.com",
  "admin": false,
  "user_id": "uuid-user-id",
  "authenticated": true
}
```

## Struktura projektu

```
/app
├── backend/
│   ├── server.py          # FastAPI z auth (JWT verify, admin_required)
│   ├── .env               # Konfiguracja z SUPABASE_JWT_SECRET, ADMIN_EMAILS
│   ├── .env.example       # Template konfiguracji
│   └── requirements.txt   # Zawiera PyJWT
│
├── frontend/
│   └── public/
│       ├── index.html     # Główna strona (React app)
│       ├── admin.html     # Panel admina (standalone)
│       ├── env.js         # Konfiguracja środowiska
│       └── env.js.template # Template konfiguracji
│
└── README_ADMIN.md        # Ten plik
```

## Zabezpieczone endpointy

Wszystkie endpointy administracyjne wymagają tokenu JWT i statusu admina:

### Ogłoszenia busów
- `POST /api/ogloszenia` - Dodaj ogłoszenie
- `GET /api/ogloszenia` - Lista wszystkich (admin)
- `PUT /api/ogloszenia/{id}` - Edytuj ogłoszenie
- `DELETE /api/ogloszenia/{id}` - Usuń ogłoszenie
- `POST /api/upload` - Upload zdjęć

### Opinie
- `POST /api/opinie` - Dodaj opinię
- `GET /api/opinie` - Lista wszystkich (admin)
- `PUT /api/opinie/{id}` - Edytuj opinię
- `DELETE /api/opinie/{id}` - Usuń opinię

### Publiczne endpointy (bez autoryzacji)
- `GET /api/ogloszenia/{id}` - Szczegóły pojedynczego busa
- `GET /api/opinie/public` - Publiczne opinie
- `GET /api/stats` - Statystyki

## Rozwiązywanie problemów

### Problem: "Invalid or expired token"

**Przyczyna:** Token JWT wygasł lub jest nieprawidłowy

**Rozwiązanie:**
1. Wyloguj się i zaloguj ponownie w panelu admina
2. Sprawdź czy `SUPABASE_JWT_SECRET` w `.env` jest poprawny

### Problem: "Admin access required"

**Przyczyna:** Email użytkownika nie jest w liście `ADMIN_EMAILS`

**Rozwiązanie:**
1. Sprawdź czy email jest dokładnie taki sam (case-insensitive)
2. Upewnij się że w `ADMIN_EMAILS` nie ma spacji między emailami
3. Restart backendu: `sudo supervisorctl restart backend`

### Problem: "SUPABASE_JWT_SECRET not configured"

**Przyczyna:** Brak zmiennej środowiskowej

**Rozwiązanie:**
1. Dodaj `SUPABASE_JWT_SECRET` do `/app/backend/.env`
2. Restart backendu

### Problem: Panel admina nie ładuje się

**Przyczyna:** Brak pliku `env.js` lub błędna konfiguracja

**Rozwiązanie:**
1. Sprawdź czy `/app/frontend/public/env.js` istnieje
2. Sprawdź czy wartości są poprawnie wypełnione (bez `${...}`)
3. Sprawdź konsolę przeglądarki (F12) dla błędów

## Uwagi bezpieczeństwa

1. **Nigdy nie commituj** plików `.env` z prawdziwymi kluczami do repozytorium
2. **SUPABASE_JWT_SECRET** trzymaj w tajemnicy - to klucz do weryfikacji tokenów
3. **ADMIN_EMAILS** - dodawaj tylko zaufane adresy email
4. Używaj HTTPS w produkcji
5. Regularnie aktualizuj hasła adminów w Supabase
6. Monitoruj logi dostępu do panelu admina

## FAQ

**Q: Jak dodać nowego admina?**  
A: Dodaj jego email do `ADMIN_EMAILS` w `.env` i zrestartuj backend

**Q: Czy mogę używać różnych tokenów JWT?**  
A: Tak, ale musisz używać Supabase jako providera autoryzacji

**Q: Jak sprawdzić czy token jest ważny?**  
A: Wywołaj `GET /api/me` - jeśli zwróci 200, token jest ważny

**Q: Jak długo token jest ważny?**  
A: Domyślnie 1 godzina (konfigurowane w Supabase)

**Q: Jak zmienić ukryty URL panelu?**  
A: Zmień `ADMIN_PATH` w `.env` i zrestartuj backend. Pamiętaj też zaktualizować `REACT_APP_ADMIN_PATH` w frontend/.env

**Q: Zapomniałem hasła dostępu do panelu**  
A: Hasło jest w pliku `/app/backend/.env` pod kluczem `ADMIN_PASSWORD`

**Q: Czy hasło dostępu jest bezpieczne?**  
A: Tak - używamy HMAC-SHA256 do podpisywania cookies. Cookie nie zawiera hasła, tylko podpis. Ale ZAWSZE zmień domyślne hasło!

**Q: Jak wylogować się z panelu?**  
A: Usuń cookie `admin_session` w przeglądarce lub poczekaj 8h (wygaśnie automatycznie)

## Bezpieczeństwo warstwy hasłowej

### Zalecenia

1. **ADMIN_PATH**: Użyj losowego ciągu (min. 16 znaków):
   ```bash
   # Przykład generowania:
   python3 -c "import secrets; print(secrets.token_urlsafe(16))"
   ```

2. **ADMIN_PASSWORD**: Silne hasło (min. 16 znaków, mix wielkich/małych liter, cyfr, znaków specjalnych)

3. **ADMIN_COOKIE_SECRET**: Losowy sekret (min. 32 znaki):
   ```bash
   # Przykład generowania:
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Regularnie zmieniaj** te wartości (np. co 3 miesiące)

5. **Nie commituj** pliku `.env` do repozytorium!

### Architektura bezpieczeństwa

```
┌──────────────────┐
│  Użytkownik      │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│ Warstwa 1: Ukryty URL + Hasło│ ← Podstawowa ochrona
│ - /admin-{ADMIN_PATH}        │
│ - Formularz hasła            │
│ - HMAC-signed cookie (8h)    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Warstwa 2: Supabase JWT      │ ← API protection
│ - JWT token verification     │
│ - ADMIN_EMAILS whitelist     │
│ - Per-endpoint authorization │
└──────────────────────────────┘
```

## Kontakt

W razie problemów sprawdź logi backendu:
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log
```

---

**Autor:** E1 Agent  
**Data:** 2025-10-21  
**Wersja:** 2.0.0 (z ukrytym URL + hasłem)
