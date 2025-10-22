# FHU FRANKO - System Zarządzania Ogłoszeniami Busów

System do zarządzania ogłoszeniami sprzedaży busów i pojazdów dostawczych dla FHU FRANKO.

## 🚀 Wdrożenie na Railway

**Szybki start:** Zobacz [RAILWAY_QUICKSTART.md](./RAILWAY_QUICKSTART.md) (5 minut)

**Pełna dokumentacja:** Zobacz [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

### ⚠️ Wymagania przed wdrożeniem:

1. **MongoDB Atlas** - darmowe konto dla bazy danych
2. **Supabase Storage** - WYMAGANE dla przechowywania zdjęć busów
   - Musisz utworzyć bucket "bus-images" jako publiczny
   - Zdjęcia NIE będą działać bez Supabase!
3. **Railway** - platforma hostingowa

## 📋 Funkcje

- ✅ Publiczna strona z listą busów
- ✅ Szczegółowe karty produktów z filtrowaniem
- ✅ Panel administracyjny z zabezpieczeniem hasłem
- ✅ Dodawanie/edycja/usuwanie ogłoszeń
- ✅ Upload zdjęć do Supabase Storage
- ✅ System opinii klientów
- ✅ Responsywny design (mobile-first)

## 🔐 Bezpieczeństwo

- Panel admina chroniony hasłem
- Ukryty URL logowania: `/admin-X9T4G7QJ2MZP8L1W3R5C6VDHY`
- Cookie-based authentication
- CORS protection
- Wszystkie wrażliwe dane w zmiennych środowiskowych

## 🛠️ Technologie

**Backend:**
- FastAPI (Python)
- MongoDB (baza danych)
- Supabase Storage (zdjęcia)
- JWT Authentication

**Frontend:**
- React 18
- Tailwind CSS
- Axios
- React Router

## 📁 Struktura projektu

```
/app/
├── backend/              # FastAPI backend
│   ├── server.py        # Główna aplikacja
│   ├── requirements.txt # Zależności Python
│   └── .env.railway.example
├── frontend/            # React frontend
│   ├── src/
│   ├── public/
│   └── .env.railway.example
├── railway.json         # Konfiguracja Railway
├── Procfile            # Railway start command
└── RAILWAY_*.md        # Dokumentacja wdrożenia
```

## 🚦 Lokalne uruchomienie (development)

Aplikacja jest skonfigurowana do uruchomienia w środowisku developerskim Emergent.

**Uruchomienie serwisów:**
```bash
sudo supervisorctl restart all
```

**Dostęp:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api
- Panel Admin: http://localhost:3000/admin-X9T4G7QJ2MZP8L1W3R5C6VDHY

## 📞 Logowanie do Panelu Admina

**URL:** `/admin-X9T4G7QJ2MZP8L1W3R5C6VDHY`
**Hasło:** `FHUfranko!%Nbzw`

⚠️ Zmień te dane na produkcji!

## 📸 Zdjęcia busów - WAŻNE!

Zdjęcia MUSZĄ być przechowywane w Supabase Storage:

1. Utwórz bucket "bus-images" w Supabase
2. Ustaw jako **PUBLIC**
3. Skonfiguruj zmienne `SUPABASE_URL` i `SUPABASE_ANON_KEY`

Bez tego zdjęcia nie będą działać na Railway!

## 🐛 Troubleshooting

Zobacz sekcję Troubleshooting w [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)

## 📄 Licencja

© 2024 FHU FRANKO. All rights reserved.
