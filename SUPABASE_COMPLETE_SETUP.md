# 🚀 Konfiguracja Supabase dla FHU FRANKO

## Czym jest Supabase?

Supabase to **"open-source Firebase alternative"** - kompletna platforma Backend-as-a-Service, która zapewnia:
- 📊 **PostgreSQL Database** - pełna baza danych SQL
- 📁 **Storage** - przechowywanie plików (zdjęć busów)
- 🔐 **Authentication** - opcjonalna autentykacja użytkowników
- 🔄 **Realtime** - live updates (nie używane w tej aplikacji)

**Dla Twojej aplikacji Supabase zastępuje:**
- ✅ MongoDB → PostgreSQL (baza danych dla busów i opinii)
- ✅ Lokalne przechowywanie → Supabase Storage (zdjęcia busów)

---

## ⚡ Szybka Konfiguracja (15 minut)

### Krok 1: Utwórz projekt Supabase (2 min)

1. Wejdź na: https://supabase.com
2. Kliknij **Start your project** → Sign in with GitHub
3. **New Project**:
   - Name: `fhu-franko`
   - Database Password: **Zapisz hasło!** (ważne dla backupów)
   - Region: Europe (Frankfurt/Ireland)
   - Free Plan
4. Poczekaj 2 minuty aż projekt się utworzy

### Krok 2: Utwórz tabele w bazie danych (3 min)

1. W projekcie Supabase → **SQL Editor** (lewa strona)
2. **New Query**
3. Skopiuj całą zawartość pliku `/app/SUPABASE_SCHEMA.sql`
4. Wklej do SQL Editor
5. Kliknij **Run** (lub Ctrl+Enter)
6. Powinno pokazać: `Success. No rows returned`

**Co zostało utworzone:**
- Tabela `buses` - wszystkie ogłoszenia busów
- Tabela `opinions` - opinie klientów
- Indeksy dla szybkich wyszukiwań
- Row Level Security (RLS) - bezpieczeństwo dostępu

### Krok 3: Utwórz bucket dla zdjęć (2 min)

1. W projekcie Supabase → **Storage** (lewa strona)
2. **Create a new bucket**:
   - Name: `bus-images`
   - ✅ **Public bucket** (ZAZNACZ!)
   - Allowed MIME types: `image/*`
   - Max file size: `5 MB` (możesz zmienić później)
3. **Create bucket**

⚠️ **WAŻNE:** Bucket MUSI być **PUBLIC**, inaczej zdjęcia nie będą widoczne na stronie!

### Krok 4: Skopiuj klucze API (2 min)

1. W projekcie Supabase → **Settings** (koło zębate na dole)
2. **API**:
   - Project URL: `https://xxxxx.supabase.co` → **SKOPIUJ**
   - anon/public key: `eyJhbGc...` → **SKOPIUJ**
   - service_role key: **NIE UŻYWAJ** (za duże uprawnienia)
3. **Database**:
   - Connection string → Postgres → **SKOPIUJ** (opcjonalne, dla backupów)

### Krok 5: Skopiuj JWT Secret (2 min)

1. Settings → **API** → **JWT Settings**
2. JWT Secret: `xxx...` → **SKOPIUJ**

**Ten klucz jest potrzebny do:**
- Weryfikacji tokenów JWT (opcjonalne logowanie przez Supabase Auth)
- Jeśli nie używasz Supabase Auth, możesz wpisać dowolny string

---

## 🔧 Konfiguracja Railway

W Railway Dashboard → Variables, dodaj:

```bash
# Supabase (WSZYSTKIE WYMAGANE!)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=twój-jwt-secret
SUPABASE_BUCKET=bus-images

# Admin Panel
ADMIN_PATH=X9T4G7QJ2MZP8L1W3R5C6VDHY
ADMIN_PASSWORD=FHUfranko!%Nbzw
ADMIN_COOKIE_SECRET=wygeneruj-losowy-32-znakowy-string
ADMIN_EMAILS=admin@twojadomena.com

# CORS (zaktualizuj po deploy)
CORS_ORIGINS=https://twoja-app.up.railway.app
```

---

## ✅ Testowanie konfiguracji

### Test 1: Sprawdź czy tabele istnieją

1. Supabase → **Table Editor**
2. Powinieneś widzieć:
   - `buses` (0 rows)
   - `opinions` (0 rows)

### Test 2: Sprawdź bucket

1. Supabase → **Storage** → `bus-images`
2. Spróbuj przesłać testowe zdjęcie:
   - Upload → wybierz plik
   - Kliknij na plik → Get public URL
   - Otwórz URL w przeglądarce - zdjęcie powinno się wyświetlić

### Test 3: Sprawdź API po deployu

Po wdrożeniu na Railway:

```bash
# Test API
curl https://twoja-app.up.railway.app/api/

# Test statystyk (powinno zwrócić 0)
curl https://twoja-app.up.railway.app/api/stats

# Test opinii publicznych (pusta tablica)
curl https://twoja-app.up.railway.app/api/opinie/public
```

---

## 📊 Dashboard Supabase - Co gdzie

| Sekcja | Co zawiera | Kiedy używać |
|--------|-----------|--------------|
| **Table Editor** | Podgląd i edycja danych | Sprawdzanie busów i opinii |
| **SQL Editor** | Wykonywanie SQL | Tworzenie tabel, migracje |
| **Storage** | Pliki (zdjęcia busów) | Sprawdzanie przesłanych zdjęć |
| **API** | Klucze i dokumentacja | Kopiowanie kluczy |
| **Database** | Connection strings | Backupy, analytics |
| **Logs** | Logi zapytań | Debugging problemów |

---

## 🎯 Przykładowe dane testowe

Po skonfigurowaniu możesz dodać testowe dane przez admin panel lub bezpośrednio w Supabase:

### Dodaj testowego busa (Table Editor):

1. Supabase → Table Editor → `buses` → **Insert row**
2. Wypełnij pola (minimalne wymagane):

```json
{
  "id": "test-bus-1",
  "marka": "Mercedes-Benz",
  "model": "Sprinter",
  "rok": 2020,
  "przebieg": 85000,
  "paliwo": "Diesel",
  "skrzynia": "Manualna",
  "cenaBrutto": 89000,
  "typNadwozia": "Furgon",
  "moc": 163,
  "normaEmisji": "Euro 6",
  "dmcKategoria": "3.5t",
  "ladownosc": 1200,
  "wyrozniowane": true,
  "nowosc": true
}
```

### Dodaj testową opinię:

```json
{
  "id": "test-opinion-1",
  "imie": "Jan",
  "nazwisko": "Kowalski",
  "rodzajFirmy": "Firma transportowa",
  "opinia": "Świetna obsługa, polecam!",
  "zakupionyPojazd": "Mercedes Sprinter 2020",
  "ocena": 5,
  "wyswietlaj": true
}
```

---

## 🐛 Troubleshooting

### Błąd: "relation buses does not exist"
**Rozwiązanie:** Nie wykonałeś SQL ze SUPABASE_SCHEMA.sql
- Wejdź do SQL Editor → wklej cały plik → Run

### Zdjęcia nie wyświetlają się
**Rozwiązanie:** Bucket nie jest publiczny
1. Storage → bus-images → Settings
2. Zaznacz "Public bucket"
3. Save

### 401 Unauthorized przy dodawaniu busów
**Przyczyny:**
1. Nie jesteś zalogowany w panelu admina
2. Błędne hasło admina
3. RLS (Row Level Security) blokuje - sprawdź policies w Database

### CORS errors
**Rozwiązanie:**
1. Zaktualizuj `CORS_ORIGINS` w Railway Variables
2. Redeploy aplikacji

---

## 📈 Monitorowanie i Limity

### Darmowy plan Supabase (Free tier):

- ✅ 500 MB Database storage (wystarczy na ~1000 busów)
- ✅ 1 GB File storage (wystarczy na ~200-300 zdjęć w HD)
- ✅ 2 GB Bandwidth/month
- ✅ 50,000 Monthly Active Users
- ✅ Social OAuth providers

### Sprawdzanie zużycia:

1. Supabase → **Settings** → **Usage**
2. Monitoruj:
   - Database size
   - Storage size
   - API requests

### Co robić gdy limit się kończy:

1. **Upgrade do Pro ($25/month)**:
   - 8 GB Database
   - 100 GB File storage
   - 50 GB Bandwidth

2. **Optymalizacja** (zanim zapłacisz):
   - Skompresuj zdjęcia przed uploadem
   - Usuń niepotrzebne dane testowe
   - Ustaw max file size w bucket settings

---

## 🔒 Bezpieczeństwo - Best Practices

### ✅ DO:
- Używaj `anon/public` key w aplikacji (bezpieczny)
- Row Level Security jest włączone (users nie mogą modyfikować danych)
- JWT Secret trzymaj w Railway Variables (nigdy w kodzie)
- Backup bazy co tydzień

### ❌ DON'T:
- NIE używaj `service_role` key w aplikacji (ma pełne uprawnienia)
- NIE commituj kluczy do GitHub
- NIE wyłączaj Row Level Security

---

## 💾 Backupy

### Automatyczne backupy (Free tier):
- Supabase robi backup co 7 dni
- Możesz restore przez Dashboard

### Ręczny backup:

```bash
# Export całej bazy
pg_dump "postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres" > backup.sql

# Import
psql "postgresql://..." < backup.sql
```

---

## 📚 Przydatne linki

- 📖 **Supabase Docs:** https://supabase.com/docs
- 🎓 **Quickstart:** https://supabase.com/docs/guides/getting-started
- 💬 **Discord Community:** https://discord.supabase.com
- 🐛 **GitHub Issues:** https://github.com/supabase/supabase/issues

---

## ✅ Gotowe!

Po wykonaniu wszystkich kroków Twoja aplikacja będzie w pełni działać z Supabase! 🎉

**Następne kroki:**
1. Push kod do GitHub
2. Railway automatycznie zrobi redeploy
3. Przetestuj dodawanie busa przez admin panel
4. Sprawdź czy zdjęcia działają

**Pytania? Problemy?** Sprawdź sekcję Troubleshooting powyżej.
