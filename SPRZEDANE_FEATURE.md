# 🔴 DODANIE OPCJI "SPRZEDANE"

## SQL do wykonania w Supabase:

```sql
-- Dodaj kolumnę "sprzedane"
ALTER TABLE buses ADD COLUMN IF NOT EXISTS sold BOOLEAN NOT NULL DEFAULT false;

-- Dodaj indeks dla wydajności
CREATE INDEX IF NOT EXISTS idx_buses_sold ON buses(sold);
```

## Co zostało zrobione:

### Backend ✅
- Dodano pole `sold` w modelach Pydantic
- Zaktualizowano mapowanie w endpointach API

### Frontend ✅
- Dodano checkbox "🔴 SPRZEDANE" w formularzu (Sekcja 4)
- Dodano czerwony overlay "SPRZEDANE" na kartach ogłoszeń
- Dodano overlay na stronie szczegółów ogłoszenia

## Jak używać:

1. **Wykonaj SQL w Supabase** (powyżej)
2. **Wdróż na Railway** (commit + push)
3. **W panelu admina:**
   - Kliknij "Edytuj" przy ogłoszeniu
   - Przejdź do sekcji 4 "Opis sprzedawcy"
   - Zaznacz checkbox "🔴 SPRZEDANE"
   - Zapisz

4. **Efekt:**
   - Na liście ogłoszeń pojawi się czerwony napis "SPRZEDANE" nachodzący na zdjęcie
   - Na stronie szczegółów także pojawi się overlay
   - Użytkownicy zobaczą, że pojazd jest już sprzedany

## Wygląd:

**Na karcie ogłoszenia:**
```
┌─────────────────────┐
│  [Zdjęcie pojazdu]  │
│                     │
│   ╔═══════════╗    │
│   ║ SPRZEDANE ║    │  ← Czerwone tło, białe litery, przekręcone -12°
│   ╚═══════════╝    │
└─────────────────────┘
```

**Checkbox w formularzu:**
```
☑ 🔴 SPRZEDANE   ← Czerwona etykieta
```

Gotowe! ✅
