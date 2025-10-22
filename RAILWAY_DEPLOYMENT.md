# 🚀 Instrukcja Wdrożenia na Railway

## Wymagania

1. Konto na [Railway.app](https://railway.app)
2. Konto MongoDB Atlas (darmowe) - [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
3. Konto Supabase (darmowe) - [supabase.com](https://supabase.com) - **WYMAGANE dla przechowywania zdjęć**

---

## Krok 1: Przygotowanie MongoDB

### Opcja A: MongoDB Atlas (zalecane)
1. Zaloguj się do [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Utwórz nowy klaster (Free tier - M0)
3. Utwórz użytkownika bazy danych:
   - Database Access → Add New Database User
   - Zapisz username i hasło
4. Dodaj dostęp z dowolnego IP:
   - Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)
5. Skopiuj Connection String:
   - Clusters → Connect → Connect your application
   - Format: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`

### Opcja B: Railway MongoDB Plugin
1. W Railway, dodaj MongoDB plugin do projektu
2. Railway automatycznie utworzy `MONGO_URL`

---

## Krok 2: Konfiguracja Supabase Storage

⚠️ **WAŻNE:** Zdjęcia busów MUSZĄ być przechowywane w Supabase Storage!

1. Zaloguj się do [Supabase](https://supabase.com)
2. Utwórz nowy projekt (lub użyj istniejącego)
3. Przejdź do **Storage** → **Create bucket**:
   - Nazwa: `bus-images`
   - Typ: **Public bucket** (zaznacz "Public bucket")
4. Skopiuj dane z **Settings → API**:
   - Project URL: `https://twojprojekt.supabase.co`
   - anon/public key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

---

## Krok 3: Wdrożenie na Railway

### 3.1 Utworzenie projektu

1. Zaloguj się do [Railway](https://railway.app)
2. Kliknij **New Project**
3. Wybierz **Deploy from GitHub repo**
4. Połącz swoje repozytorium GitHub
5. Railway automatycznie wykryje Dockerfile i rozpocznie budowanie
   - Aplikacja używa Dockerfile dla pełnej kontroli nad buildem
   - Frontend jest budowany i serwowany przez backend FastAPI

### 3.2 Konfiguracja zmiennych środowiskowych

W Railway Dashboard → twój projekt → **Variables**, dodaj:

#### Backend Variables (wszystkie wymagane):

```bash
# MongoDB
MONGO_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
DB_NAME=busfleet_prod

# Supabase Storage (WYMAGANE dla zdjęć!)
SUPABASE_URL=https://twojprojekt.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=twoj-jwt-secret-z-supabase
SUPABASE_BUCKET=bus-images

# Admin Panel Security
ADMIN_PATH=X9T4G7QJ2MZP8L1W3R5C6VDHY
ADMIN_PASSWORD=FHUfranko!%Nbzw
ADMIN_COOKIE_SECRET=wygeneruj-bezpieczny-string-min-32-znaki
ADMIN_EMAILS=admin@twojadomena.pl

# CORS (Railway automatycznie generuje URL)
CORS_ORIGINS=https://twoja-aplikacja.up.railway.app

# Port (Railway ustawia automatycznie)
PORT=8001
```

#### Frontend Variables:

```bash
# Backend URL (zmień na URL Railway po wdrożeniu)
REACT_APP_BACKEND_URL=https://twoja-aplikacja.up.railway.app

# Admin
REACT_APP_ADMIN_PATH=X9T4G7QJ2MZP8L1W3R5C6VDHY

# Opcjonalne
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=true
```

### 3.3 Konfiguracja domeny (opcjonalne)

1. W Railway Dashboard → Settings → Domains
2. Kliknij **Generate Domain** (darmowa subdomena Railway)
3. Lub podłącz własną domenę

---

## Krok 4: Aktualizacja CORS po wdrożeniu

Po wdrożeniu, zaktualizuj zmienną `CORS_ORIGINS` z rzeczywistym URL:

```bash
CORS_ORIGINS=https://twoja-aplikacja.up.railway.app,https://twojadomena.pl
```

Możesz dodać wiele domen oddzielonych przecinkami.

---

## Krok 5: Weryfikacja

### Sprawdź czy aplikacja działa:

1. **Strona główna:** `https://twoja-aplikacja.up.railway.app/`
2. **API Health:** `https://twoja-aplikacja.up.railway.app/api/`
3. **Statystyki:** `https://twoja-aplikacja.up.railway.app/api/stats`
4. **Logowanie admin:** `https://twoja-aplikacja.up.railway.app/admin-X9T4G7QJ2MZP8L1W3R5C6VDHY`

### Test dodawania zdjęć:

1. Zaloguj się do panelu admina
2. Dodaj nowy bus ze zdjęciem
3. Sprawdź czy zdjęcie się wyświetla na stronie głównej
4. Sprawdź w Supabase Storage → bus-images czy plik został przesłany

---

## ⚠️ Ważne Uwagi

### Zdjęcia busów:
- **MUSISZ** skonfigurować Supabase Storage
- Lokalny storage **NIE DZIAŁA** na Railway (pliki znikają po restarcie)
- Bucket "bus-images" musi być **publiczny**

### Bezpieczeństwo:
- Zmień `ADMIN_PASSWORD` i `ADMIN_PATH` na produkcji
- Użyj silnego `ADMIN_COOKIE_SECRET` (min 32 znaki)
- Nigdy nie commituj plików `.env` do repozytorium

### MongoDB:
- Regularnie twórz backupy bazy danych
- Monitoruj zużycie w MongoDB Atlas

### Performance:
- Railway oferuje darmowy tier z limitami
- Monitoruj zużycie zasobów w Railway Dashboard

---

## 🐛 Troubleshooting

### Aplikacja nie startuje:
- Sprawdź logi w Railway Dashboard
- Upewnij się że wszystkie zmienne są ustawione
- Sprawdź czy MongoDB connection string jest poprawny

### Zdjęcia się nie wyświetlają:
- Sprawdź czy bucket "bus-images" istnieje w Supabase
- Sprawdź czy bucket jest **publiczny**
- Zweryfikuj `SUPABASE_URL` i `SUPABASE_ANON_KEY`
- Sprawdź logi backendu w Railway

### Błąd CORS:
- Zaktualizuj `CORS_ORIGINS` z rzeczywistym URL Railway
- Upewnij się że nie ma literówek w URL
- Dodaj zarówno domenę Railway jak i własną domenę

### 401 błędy w panelu admina:
- Sprawdź czy ciasteczka są włączone w przeglądarce
- Sprawdź czy `ADMIN_PASSWORD` jest poprawne
- Wyczyść cache i ciasteczka przeglądarki

---

## 📞 Wsparcie

- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs
- MongoDB Docs: https://docs.mongodb.com

---

## 📝 Checklist przed wdrożeniem

- [ ] MongoDB Atlas skonfigurowany i connection string skopiowany
- [ ] Supabase projekt utworzony
- [ ] Bucket "bus-images" utworzony jako publiczny w Supabase
- [ ] Wszystkie zmienne środowiskowe ustawione w Railway
- [ ] ADMIN_PASSWORD i ADMIN_PATH zmienione na bezpieczne wartości
- [ ] Kod wypushowany do GitHub
- [ ] Railway projekt podłączony do repozytorium
- [ ] CORS_ORIGINS zaktualizowany z URL Railway
- [ ] Przetestowane dodawanie busów ze zdjęciami
- [ ] Przetestowane logowanie do panelu admina
- [ ] Przetestowane wyświetlanie zdjęć na stronie

---

Gotowe! Twoja aplikacja powinna działać na Railway. 🎉
