# ✅ Railway Deployment Checklist

## Przed rozpoczęciem wdrożenia

- [ ] Mam konto GitHub i kod jest w repozytorium
- [ ] Mam konto Railway (https://railway.app)
- [ ] Mam konto MongoDB Atlas (https://mongodb.com/cloud/atlas)
- [ ] Mam konto Supabase (https://supabase.com)

## Krok 1: MongoDB Atlas Setup

- [ ] Utworzyłem klaster MongoDB (Free tier M0)
- [ ] Utworzyłem użytkownika bazy danych
- [ ] Dodałem IP 0.0.0.0/0 w Network Access
- [ ] Skopiowałem connection string
- [ ] Przetestowałem connection string (opcjonalne)

## Krok 2: Supabase Setup ⚠️ KRYTYCZNE

- [ ] Utworzyłem projekt w Supabase
- [ ] Utworzyłem bucket "bus-images"
- [ ] ✅ Bucket jest PUBLIC (bardzo ważne!)
- [ ] Skopiowałem SUPABASE_URL
- [ ] Skopiowałem SUPABASE_ANON_KEY
- [ ] Skopiowałem SUPABASE_JWT_SECRET

## Krok 3: Railway Project Setup

- [ ] Utworzyłem nowy projekt w Railway
- [ ] Połączyłem z repozytorium GitHub
- [ ] Railway rozpoczął automatyczny build

## Krok 4: Railway Variables - Backend

W Railway Variables, dodałem:

- [ ] MONGO_URL (z MongoDB Atlas)
- [ ] DB_NAME (np. busfleet_prod)
- [ ] SUPABASE_URL
- [ ] SUPABASE_ANON_KEY
- [ ] SUPABASE_JWT_SECRET
- [ ] SUPABASE_BUCKET=bus-images
- [ ] ADMIN_PATH (zmieniony na unikalny)
- [ ] ADMIN_PASSWORD (zmieniony na silny)
- [ ] ADMIN_COOKIE_SECRET (min 32 znaki)
- [ ] ADMIN_EMAILS (twój email admina)
- [ ] PORT=8001

## Krok 5: Railway Variables - Frontend

- [ ] REACT_APP_ADMIN_PATH (taki sam jak ADMIN_PATH)
- [ ] WDS_SOCKET_PORT=443
- [ ] REACT_APP_ENABLE_VISUAL_EDITS=false
- [ ] ENABLE_HEALTH_CHECK=true

## Krok 6: CORS Configuration (po pierwszym wdrożeniu)

- [ ] Skopiowałem URL Railway (np. https://twoja-app.up.railway.app)
- [ ] Zaktualizowałem CORS_ORIGINS w Railway Variables
- [ ] Zaktualizowałem REACT_APP_BACKEND_URL w Railway Variables
- [ ] Zrestartowałem deployment w Railway

## Krok 7: Testowanie

- [ ] Strona główna ładuje się poprawnie
- [ ] API endpoint działa (https://twoja-app.up.railway.app/api/)
- [ ] Statystyki działają (/api/stats)
- [ ] Mogę się zalogować do panelu admina
- [ ] Mogę dodać nowy bus
- [ ] Mogę przesłać zdjęcie
- [ ] ✅ Zdjęcie wyświetla się na stronie głównej (sprawdź w Supabase Storage czy plik został przesłany)
- [ ] Mogę edytować bus
- [ ] Mogę usunąć bus
- [ ] Mogę dodać opinię
- [ ] Opinie wyświetlają się na stronie /opinie
- [ ] Filtry na /ogloszenia działają

## Krok 8: Finalne sprawdzenie

- [ ] Zdjęcia busów wyświetlają się poprawnie (najważniejsze!)
- [ ] Brak błędów CORS w konsoli przeglądarki
- [ ] Wszystkie linki działają
- [ ] Responsywność na mobile
- [ ] Przetestowałem na różnych przeglądarkach

## Problemy? Zobacz Troubleshooting

Jeśli coś nie działa, sprawdź:
1. Logi w Railway Dashboard
2. Console w przeglądarce (F12)
3. Supabase Dashboard → Storage → bus-images
4. MongoDB Atlas → Database → Collections

Szczegóły: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

---

## 🎉 Gotowe!

Twoja aplikacja jest live na Railway!

**Następne kroki:**
- [ ] Skonfiguruj własną domenę (opcjonalne)
- [ ] Skonfiguruj backupy MongoDB
- [ ] Monitoruj zużycie w Railway Dashboard
- [ ] Regularnie sprawdzaj logi

---

Data wdrożenia: _________________
Railway URL: _________________
Admin URL: _________________/admin-{ADMIN_PATH}
