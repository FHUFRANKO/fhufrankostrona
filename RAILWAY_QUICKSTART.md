# 🚂 Szybki Start - Railway Deployment

## ⚡ W 5 krokach:

### 1️⃣ MongoDB (2 minuty)
- Utwórz darmowe konto: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
- Utwórz klaster (M0 Free)
- Dodaj użytkownika bazy danych
- Allow access from anywhere (0.0.0.0/0)
- Skopiuj connection string

### 2️⃣ Supabase - WYMAGANE dla zdjęć! (3 minuty)
- Utwórz konto: [Supabase](https://supabase.com)
- Nowy projekt
- Storage → Create bucket:
  - Nazwa: **bus-images**
  - ✅ **Public bucket** (zaznacz!)
- Skopiuj: Project URL i anon key

### 3️⃣ Railway (2 minuty)
- Zaloguj: [Railway](https://railway.app)
- New Project → Deploy from GitHub
- Wybierz swoje repo
- Railway użyje Dockerfile do zbudowania aplikacji

### 4️⃣ Zmienne środowiskowe w Railway
Wklej w Variables (zakładka):

```bash
# MongoDB
MONGO_URL=twój-connection-string-z-mongodb-atlas
DB_NAME=busfleet_prod

# Supabase (WYMAGANE!)
SUPABASE_URL=https://twojprojekt.supabase.co
SUPABASE_ANON_KEY=twój-anon-key
SUPABASE_JWT_SECRET=twój-jwt-secret
SUPABASE_BUCKET=bus-images

# Admin
ADMIN_PATH=X9T4G7QJ2MZP8L1W3R5C6VDHY
ADMIN_PASSWORD=FHUfranko!%Nbzw
ADMIN_COOKIE_SECRET=wygeneruj-losowy-32-znakowy-string

# CORS (zaktualizuj po deployment)
CORS_ORIGINS=https://twoja-app.up.railway.app

# Frontend
REACT_APP_BACKEND_URL=https://twoja-app.up.railway.app
REACT_APP_ADMIN_PATH=X9T4G7QJ2MZP8L1W3R5C6VDHY
```

### 5️⃣ Deploy & Test
- Railway automatycznie zbuduje aplikację
- Po zakończeniu, otwórz URL Railway
- Przetestuj dodawanie busa ze zdjęciem

## ✅ Gotowe!

Szczegóły: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

---

## ⚠️ Najczęstsze Błędy

❌ **Zdjęcia nie działają**
→ Sprawdź czy utworzyłeś bucket "bus-images" w Supabase jako **PUBLIC**

❌ **500 błąd przy starcie**
→ Sprawdź czy `MONGO_URL` jest poprawny w Railway Variables

❌ **CORS błędy**
→ Zaktualizuj `CORS_ORIGINS` z prawdziwym URL Railway
