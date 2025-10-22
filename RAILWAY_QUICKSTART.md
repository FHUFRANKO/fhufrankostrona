# 🚂 Szybki Start - Railway Deployment

## ⚡ W 5 krokach:

### 1️⃣ Supabase - WYMAGANE! (15 minut)
**Supabase zapewnia bazę danych (PostgreSQL) + storage dla zdjęć**

- Utwórz konto: [Supabase](https://supabase.com)
- Nowy projekt
- SQL Editor → wklej `SUPABASE_SCHEMA.sql` → Run
- Storage → Create bucket:
  - Nazwa: **bus-images**
  - ✅ **Public bucket** (zaznacz!)
- Skopiuj: Project URL, anon key, JWT secret

📖 **Szczegóły:** [SUPABASE_COMPLETE_SETUP.md](./SUPABASE_COMPLETE_SETUP.md)

### 2️⃣ Railway (2 minuty)
- Zaloguj: [Railway](https://railway.app)
- New Project → Deploy from GitHub
- Wybierz swoje repo
- Railway użyje Dockerfile do zbudowania aplikacji

### 4️⃣ Zmienne środowiskowe w Railway
Wklej w Variables (zakładka):

```bash
# Supabase (WSZYSTKIE WYMAGANE!)
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
