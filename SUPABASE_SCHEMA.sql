-- FHU FRANKO Database Schema for Supabase PostgreSQL
-- Run this in Supabase SQL Editor

-- Create buses table
CREATE TABLE IF NOT EXISTS buses (
    id TEXT PRIMARY KEY,
    marka TEXT NOT NULL,
    model TEXT NOT NULL,
    rok INTEGER NOT NULL,
    przebieg INTEGER NOT NULL,
    paliwo TEXT NOT NULL,
    skrzynia TEXT NOT NULL,
    naped TEXT,
    "cenaBrutto" INTEGER NOT NULL,
    "cenaNetto" INTEGER,
    vat BOOLEAN DEFAULT true,
    "typNadwozia" TEXT NOT NULL,
    moc INTEGER NOT NULL,
    kubatura INTEGER,
    "normaSpalania" TEXT,
    "normaEmisji" TEXT NOT NULL,
    "dmcKategoria" TEXT NOT NULL,
    ladownosc INTEGER NOT NULL,
    "wymiarL" TEXT,
    "wymiarH" TEXT,
    "liczbaMiejsc" INTEGER,
    "liczbaPalet" INTEGER,
    klima BOOLEAN DEFAULT false,
    tempomat BOOLEAN DEFAULT false,
    kamera BOOLEAN DEFAULT false,
    "czujnikiParkowania" BOOLEAN DEFAULT false,
    hak BOOLEAN DEFAULT false,
    "asystentPasa" BOOLEAN DEFAULT false,
    bluetooth BOOLEAN DEFAULT false,
    opis TEXT,
    wyposazenie JSONB DEFAULT '[]'::jsonb,
    zdjecia JSONB DEFAULT '[]'::jsonb,
    "zdjecieGlowne" TEXT,
    wyrozniowane BOOLEAN DEFAULT false,
    nowosc BOOLEAN DEFAULT false,
    flotowy BOOLEAN DEFAULT false,
    gwarancja BOOLEAN DEFAULT false,
    "numerOgloszenia" TEXT,
    "dataPublikacji" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create opinions table
CREATE TABLE IF NOT EXISTS opinions (
    id TEXT PRIMARY KEY,
    imie TEXT NOT NULL,
    nazwisko TEXT NOT NULL,
    "rodzajFirmy" TEXT NOT NULL,
    opinia TEXT NOT NULL,
    "zakupionyPojazd" TEXT NOT NULL,
    ocena INTEGER DEFAULT 5,
    wyswietlaj BOOLEAN DEFAULT true,
    "dataPublikacji" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_buses_rok ON buses(rok);
CREATE INDEX IF NOT EXISTS idx_buses_marka ON buses(marka);
CREATE INDEX IF NOT EXISTS idx_buses_wyrozniowane ON buses(wyrozniowane);
CREATE INDEX IF NOT EXISTS idx_buses_nowosc ON buses(nowosc);
CREATE INDEX IF NOT EXISTS idx_buses_flotowy ON buses(flotowy);
CREATE INDEX IF NOT EXISTS idx_buses_dataPublikacji ON buses("dataPublikacji");

CREATE INDEX IF NOT EXISTS idx_opinions_wyswietlaj ON opinions(wyswietlaj);
CREATE INDEX IF NOT EXISTS idx_opinions_dataPublikacji ON opinions("dataPublikacji");

-- Enable Row Level Security (RLS)
ALTER TABLE buses ENABLE ROW LEVEL SECURITY;
ALTER TABLE opinions ENABLE ROW LEVEL SECURITY;

-- Public read access for buses
CREATE POLICY "Public read access for buses" ON buses
    FOR SELECT
    USING (true);

-- Authenticated users can insert/update/delete buses
CREATE POLICY "Authenticated users can insert buses" ON buses
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Authenticated users can update buses" ON buses
    FOR UPDATE
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can delete buses" ON buses
    FOR DELETE
    TO authenticated
    USING (true);

-- Public read access for visible opinions
CREATE POLICY "Public read access for visible opinions" ON opinions
    FOR SELECT
    USING (wyswietlaj = true);

-- Authenticated users can manage all opinions
CREATE POLICY "Authenticated users can read all opinions" ON opinions
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can insert opinions" ON opinions
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Authenticated users can update opinions" ON opinions
    FOR UPDATE
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can delete opinions" ON opinions
    FOR DELETE
    TO authenticated
    USING (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_buses_updated_at BEFORE UPDATE ON buses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_opinions_updated_at BEFORE UPDATE ON opinions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
