// Mock data for FHU FRANKO – Autohandel BUSY/DOSTAWCZE marketplace

export const marki = [
  'Mercedes-Benz', 'Ford', 'Volkswagen', 'Iveco', 'Renault', 'Peugeot', 
  'Fiat', 'Opel', 'MAN', 'Volvo', 'Scania', 'DAF', 'Isuzu', 'Mitsubishi'
];

export const modele = {
  'Mercedes-Benz': ['Sprinter', 'Vito', 'Viano', 'Citan', 'Atego', 'Actros'],
  'Ford': ['Transit', 'Transit Custom', 'Transit Connect', 'Tourneo Custom', 'Tourneo Connect'],
  'Volkswagen': ['Crafter', 'Caddy', 'T6 Transporter', 'T6 Caravelle', 'T6 Multivan'],
  'Iveco': ['Daily', 'Eurocargo', 'Stralis', 'S-Way', 'Turbodaily'],
  'Renault': ['Master', 'Trafic', 'Kangoo', 'Maxity', 'D-Truck'],
  'Peugeot': ['Boxer', 'Expert', 'Partner', 'Bipper'],
  'Fiat': ['Ducato', 'Scudo', 'Doblo', 'Fiorino'],
  'Opel': ['Movano', 'Vivaro', 'Combo'],
  'MAN': ['TGE', 'TGM', 'TGS', 'TGX'],
  'Volvo': ['FH', 'FM', 'FE', 'FL'],
  'Scania': ['R-Series', 'S-Series', 'P-Series', 'G-Series'],
  'DAF': ['XF', 'CF', 'LF'],
  'Isuzu': ['N-Series', 'F-Series', 'D-Max'],
  'Mitsubishi': ['Fuso Canter', 'L200']
};

export const paliwa = ['Diesel', 'CNG', 'LPG', 'Elektryczny', 'Hybryda Diesel'];
export const skrzynie = ['Manualna', 'Automatyczna', 'Półautomatyczna', 'AMT'];
export const napedy = ['Przedni (FWD)', 'Tylni (RWD)', '4x4 (AWD)'];

// Typy nadwozi specyficzne dla busów/LCV
export const typyNadwozi = [
  'Furgon', 
  'Kontener', 
  'Plandeka', 
  'Skrzynia', 
  'Chłodnia', 
  'Minibus', 
  'Brygadowy', 
  'Doka', 
  'Osobowe'
];

// Masy całkowite (DMC)
export const dmcKategorie = [
  'do 3.5t',
  '3.5-7.5t', 
  'powyżej 7.5t'
];

// Wymiary L x H (długość x wysokość)
export const wymiary = {
  'L1': '4963mm',
  'L2': '5531mm', 
  'L3': '6036mm',
  'L4': '6940mm',
  'H1': '1940mm',
  'H2': '2150mm',
  'H3': '2370mm'
};

// Normy emisji
export const normyEmisji = ['Euro 4', 'Euro 5', 'Euro 6'];

export const kolory = ['Biały', 'Czarny', 'Szary', 'Srebrny', 'Niebieski', 'Czerwony', 'Żółty', 'Pomarańczowy'];

// Prawdziwe zdjęcia busów
const busPhotos = {
  furgon: [
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/x95quwic_525300848_122105401868956303_2895063514729956344_n.jpg', // Ford Transit biały
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/5bhqz75g_525859179_122105398262956303_912120270446366251_n.jpg', // Nissan NV400 długi
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/4yxi5evl_526095088_122105405672956303_4191033354436590793_n.jpg'  // Opel Vivaro czerwony
  ],
  kontener: [
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/zce3dsmt_526069192_122105396444956303_5557111824766637735_n.jpg', // Renault Master z kontenerem
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/5bhqz75g_525859179_122105398262956303_912120270446366251_n.jpg'  // Nissan NV400 długi
  ],
  brygadowy: [
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/0oses8qw_526277493_122105399882956303_1812905206658123256_n.jpg', // Renault Master minibus
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/4yxi5evl_526095088_122105405672956303_4191033354436590793_n.jpg'  // Opel Vivaro czerwony
  ],
  minibus: [
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/0oses8qw_526277493_122105399882956303_1812905206658123256_n.jpg', // Renault Master minibus
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/x95quwic_525300848_122105401868956303_2895063514729956344_n.jpg'  // Ford Transit 
  ],
  default: [
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/x95quwic_525300848_122105401868956303_2895063514729956344_n.jpg', // Ford Transit
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/5bhqz75g_525859179_122105398262956303_912120270446366251_n.jpg', // Nissan NV400
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/zce3dsmt_526069192_122105396444956303_5557111824766637735_n.jpg', // Renault Master kontener
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/4yxi5evl_526095088_122105405672956303_4191033354436590793_n.jpg', // Opel Vivaro
    'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/0oses8qw_526277493_122105399882956303_1812905206658123256_n.jpg'  // Renault Master minibus
  ]
};

export const miasta = [ 
  'Katowice', 'Lublin', 'Białystok', 'Szczecin', 'Bydgoszcz', 'Olsztyn'
];

// Wyposażenie specyficzne dla busów/LCV - rozszerzone zgodnie z wymaganiami
export const wyposazenie = {
  'Bezpieczeństwo / układy': [
    'ABS', 'ASR', 'alarm', 'immobilizer', 'poduszka powietrzna kierowcy', 'poduszka powietrzna pasażera'
  ],
  'Komfort / sterowanie': [
    'klimatyzacja', 'webasto', 'podgrzewane siedzenia', 'elektryczne szyby', 
    'elektryczne lusterka', 'centralny zamek', 'wspomaganie kierownicy', 
    'fotel pneumatyczny', 'komputer pokładowy'
  ],
  'Asysta / infotainment': [
    'tempomat', 'czujniki parkowania', 'kamera cofania', 'nawigacja GPS', 
    'radio', 'bluetooth', 'wielofunkcyjna kierownica'
  ],
  'Nadwozie / dostęp': [
    'przesuwane drzwi', 'tylne drzwi skrzydełka', 'drzwi tylne 360°', 
    'klapa bagażnika', 'halogeny', 'oświetlenie przestrzeni bagażowej'
  ]
};

// Typy drzwi dla busów
export const drzwi = [
  'Boczne prawe',
  'Boczne lewe', 
  'Boczne obustronne',
  'Tylne dwuskrzydłowe',
  'Tylne podnośna brama',
  'Przesuwne boczne'
];

// Funkcja dobierająca zdjęcia do typu nadwozia
const getPhotosForBodyType = (typNadwozia) => {
  if (typNadwozia === 'Furgon') return busPhotos.furgon;
  if (typNadwozia === 'Kontener' || typNadwozia === 'Skrzynia') return busPhotos.kontener;
  if (typNadwozia === 'Brygadowy (5-7 miejsc)') return busPhotos.brygadowy;
  if (typNadwozia === 'Minibus (9-20 miejsc)') return busPhotos.minibus;
  return busPhotos.default;
};

// Generate mock bus/LCV listings
export const generateMockBuses = (count = 50) => {
  const buses = [];
  
  for (let i = 0; i < count; i++) {
    const marka = marki[Math.floor(Math.random() * marki.length)];
    const dostepneModele = modele[marka];
    const model = dostepneModele[Math.floor(Math.random() * dostepneModele.length)];
    const rok = 2016 + Math.floor(Math.random() * 9); // 2016-2024
    const przebieg = Math.floor(Math.random() * 300000) + 20000; // 20k-320k km
    const cena = 34567; // Stała cena dla wszystkich busów
    
    const typNadwozia = typyNadwozi[Math.floor(Math.random() * typyNadwozi.length)];
    const dmcValue = Math.random() > 0.7 ? (Math.random() > 0.5 ? 5500 : 8500) : 3500;
    const dmcKategoria = dmcValue <= 3500 ? 'do 3.5t' : dmcValue <= 7500 ? '3.5-7.5t' : 'powyżej 7.5t';
    
    const lDim = ['L1', 'L2', 'L3', 'L4'][Math.floor(Math.random() * 4)];
    const hDim = ['H1', 'H2', 'H3'][Math.floor(Math.random() * 3)];
    
    const ladownosc = Math.floor(dmcValue * 0.4) + Math.floor(Math.random() * 500);
    const kubatura = Math.floor(Math.random() * 15) + 3; // 3-18 m³
    
    // Wyposażenie użytkowe
    const winda = Math.random() > 0.7;
    const hak = Math.random() > 0.6;
    const klimatyzacjaLadunkowa = Math.random() > 0.8;
    const przegroda = Math.random() > 0.5;
    const twinWheel = dmcValue > 3500 && Math.random() > 0.7;
    const czterykola = Math.random() > 0.9;
    const flotowy = Math.random() > 0.6;
    
    const bus = {
      id: i + 1,
      numerOgloszenia: `FKBUS${String(i + 1).padStart(5, '0')}`,
      marka,
      model,
      wersja: `${model} ${Math.floor(Math.random() * 3) + 2}.${Math.floor(Math.random() * 5)}L`,
      rok,
      pierwszaRejestracja: `${rok}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}`,
      przebieg,
      paliwo: paliwa[Math.floor(Math.random() * paliwa.length)],
      skrzynia: skrzynie[Math.floor(Math.random() * skrzynie.length)],
      naped: napedy[Math.floor(Math.random() * napedy.length)],
      
      // Parametry specyficzne dla busów/LCV
      typNadwozia,
      dmc: dmcValue,
      dmcKategoria,
      ladownosc,
      kubatura,
      wymiarL: lDim,
      wymiarH: hDim,
      wymiarLMm: parseInt(wymiary[lDim].replace('mm', '')),
      wymiarHMm: parseInt(wymiary[hDim].replace('mm', '')),
      
      // Wymiary paki (mm)
      wymiaryPaki: {
        dlugosc_mm: typNadwozia === 'Furgon' || typNadwozia === 'Kontener' ? 2800 + Math.floor(Math.random() * 1500) : null,
        szerokosc_mm: typNadwozia === 'Furgon' || typNadwozia === 'Kontener' ? 1600 + Math.floor(Math.random() * 200) : null,
        szerokosc_miedzy_nadkolami_mm: typNadwozia === 'Furgon' || typNadwozia === 'Kontener' ? 1200 + Math.floor(Math.random() * 150) : null,
        wysokosc_mm: typNadwozia === 'Furgon' || typNadwozia === 'Kontener' ? 1700 + Math.floor(Math.random() * 400) : null
      },
      
      moc: Math.floor(Math.random() * 100) + 90, // 90-190 KM
      pojemnosc: Math.floor(Math.random() * 1000) + 1500, // 1.5-2.5L
      kolor: kolory[Math.floor(Math.random() * kolory.length)],
      normaEmisji: normyEmisji[Math.floor(Math.random() * normyEmisji.length)],
      adBlue: Math.random() > 0.6,
      
      cenaBrutto: cena,
      cenaNetto: Math.floor(cena * 0.81),
      vat: true,
      lokalizacja: miasta[Math.floor(Math.random() * miasta.length)],
      gwarancja: Math.random() > 0.5,
      wyroznialone: Math.random() > 0.8,
      nowosc: Math.random() > 0.85,
      flotowy,
      
      // Wyposażenie użytkowe
      winda,
      hak,
      klimatyzacjaLadunkowa,
      przegroda,
      twinWheel,
      czterykola,
      
      zdjecia: (() => {
        const photosForType = getPhotosForBodyType(typNadwozia);
        const selectedPhoto = photosForType[Math.floor(Math.random() * photosForType.length)];
        return [selectedPhoto, selectedPhoto, selectedPhoto]; // 3x to samo zdjęcie dla prostoty
      })(),
      
      opis: `Profesjonalny ${typNadwozia.toLowerCase()} w doskonałym stanie technicznym. ${
        flotowy ? 'Pojazd po leasingu flotowym z udokumentowaną historią serwisową.' : 'Regularnie serwisowany, bezwypadkowy.'
      } Idealny do pracy w ${typNadwozia === 'Furgon' ? 'logistyce i transporcie' : 
                         typNadwozia === 'Chłodnia' ? 'transporcie żywności' :
                         typNadwozia === 'Brygadowy (5-7 miejsc)' ? 'przewozie ekip roboczych' :
                         'zastosowaniach komercyjnych'}.`,
      
      // Szczegółowe wyposażenie - nowe kategorie
      wyposazenie: {
        'Bezpieczeństwo / układy': wyposazenie['Bezpieczeństwo / układy'].slice(0, Math.floor(Math.random() * 4) + 2),
        'Komfort / sterowanie': wyposazenie['Komfort / sterowanie'].slice(0, Math.floor(Math.random() * 6) + 3),
        'Asysta / infotainment': wyposazenie['Asysta / infotainment'].slice(0, Math.floor(Math.random() * 5) + 2),
        'Nadwozie / dostęp': wyposazenie['Nadwozie / dostęp'].slice(0, Math.floor(Math.random() * 4) + 2)
      },
      
      // Hak jako osobna flaga
      hak,
      
      drzwi: drzwi[Math.floor(Math.random() * drzwi.length)],
      
      kontakt: {
        nazwa: 'FHU FRANKO – Autohandel BUSY/DOSTAWCZE',
        telefon: '+48 123 456 789',
        email: 'busy@fhufranko.pl',
        godziny: 'Pn-Pt: 8:00-18:00, Sb: 9:00-15:00'
      },
      dataPublikacji: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000),
      status: 'aktywne'
    };
    
    buses.push(bus);
  }
  
  return buses;
};

export const mockBuses = generateMockBuses();

// Mock reviews/opinions - zaktualizowane pod BUSY/DOSTAWCZE
export const mockOpinie = [
  {
    id: 1,
    autor: 'Marek K.',
    branza: 'Transport i logistyka',
    ocena: 5,
    komentarz: 'Doskonały furgon do pracy miejskiej. Wszystkie serwisy udokumentowane, auto bez wkładu finansowego. Bardzo profesjonalna obsługa.',
    data: '2024-02-15'
  },
  {
    id: 2,
    autor: 'Anna S.',
    branza: 'Usługi kurierskie',
    ocena: 5,
    komentarz: 'Szybka realizacja zakupu, bus idealny do dostaw miejskich. Polecam każdemu kto szuka niezawodnego auta dostawczego.',
    data: '2024-02-20'
  },
  {
    id: 3,
    autor: 'Tomasz W.',
    branza: 'Budownictwo',
    ocena: 5,
    komentarz: 'Solidny brygadowy, wygodny dla całej ekipy. Świetna cena za stan techniczny, wszystko zgodnie z opisem.',
    data: '2024-03-05'
  },
  {
    id: 4,
    autor: 'Karolina M.',
    branza: 'Handel detaliczny',
    ocena: 4,
    komentarz: 'Bardzo dobry kontakt z firmą, szybkie załatwienie formalności. Bus spełnia wszystkie oczekiwania.',
    data: '2024-03-12'
  },
  {
    id: 5,
    autor: 'Piotr Z.',
    branza: 'Usługi remontowe',
    ocena: 5,
    komentarz: 'Auto jak z salonu, pełna dokumentacja serwisowa. Polecam FHU FRANKO za rzetelność i profesjonalizm.',
    data: '2024-03-18'
  },
  {
    id: 6,
    autor: 'Michał D.',
    branza: 'Catering',
    ocena: 5,
    komentarz: 'Idealne auto do przewozu żywności. Klimatyzacja ładunkowa działała bez zarzutu. Bardzo zadowolony z obsługi.',
    data: '2024-03-22'
  },
  {
    id: 7,
    autor: 'Agnieszka L.',
    branza: 'E-commerce',
    ocena: 4,
    komentarz: 'Sprawny proces zakupu, auto odpowiadało dokładnie opisowi. Miła i kompetentna obsługa klienta.',
    data: '2024-04-02'
  },
  {
    id: 8,
    autor: 'Robert K.',
    branza: 'Usługi instalacyjne',
    ocena: 5,
    komentarz: 'Bus z windą załadowczą to było dokładnie to czego szukałem. Świetny stan techniczny, polecam!',
    data: '2024-04-08'
  },
  {
    id: 9,
    autor: 'Magdalena P.',
    branza: 'Kwiaciarnia',
    ocena: 5,
    komentarz: 'Kompaktowy furgon idealny do dostaw kwiatów po mieście. Niskie spalanie, bardzo ekonomiczny.',
    data: '2024-04-15'
  },
  {
    id: 10,
    autor: 'Janusz B.',
    branza: 'Chłodnictwo',
    ocena: 4,
    komentarz: 'Solidne auto do przewozu sprzętu chłodniczego. Wszystko załatwione sprawnie i bez problemów.',
    data: '2024-04-20'
  },
  {
    id: 11,
    autor: 'Katarzyna R.',
    branza: 'Usługi sprzątające',
    ocena: 5,
    komentarz: 'Przestronny bus, zmieści cały sprzęt do sprzątania. Przegroda kabiny bardzo praktyczna.',
    data: '2024-04-25'
  },
  {
    id: 12,
    autor: 'Łukasz G.',
    branza: 'Elektryk',
    ocena: 5,
    komentarz: 'Wysokość ładunkowa wystarczająca dla długich rur i kabli. Auto w doskonałym stanie technicznym.',
    data: '2024-05-03'
  }
];

// Mock services - tylko dla busów/LCV (bez finansowania/serwisu)
export const mockUslugi = [
  {
    id: 'busy-dostawcze',
    tytul: 'Busy Dostawcze',
    opis: 'Furgony, kontenery, plandeki, skrzynie- pojazdy do transportu towarów',
    ikona: 'Truck'
  },
  {
    id: 'busy-osobowe', 
    tytul: 'Brygadowe i osobowe',
    opis: 'Brygadowe, doki do przewozu towarów i pasażerów',
    ikona: 'Users'
  },
  {
    id: 'specjalistyczne',
    tytul: 'Pojazdy Specjalistyczne', 
    opis: 'Chłodnie, lawety, wywrotki, maszyny i inne',
    ikona: 'Settings'
  }
];

export const mockPrzewagi = [
  {
    ikona: 'Settings',
    tytul: 'Specjalizacja w Pojazdach Użytkowych', 
    opis: 'Profesjonalne doradztwo w wyborze busa do pracy i obsługa'
  },
  {
    ikona: 'Clock',
    tytul: 'Natychmiastowa Dostępność',
    opis: 'Busy gotowe do pracy od zaraz – nie czekaj na zamówienie'
  },
  {
    ikona: 'Truck',
    tytul: 'Dostawa pod dom',
    opis: 'Oferujemy bezpieczny transport auta pod Twoją firmę lub dom'
  },
  {
    ikona: 'Globe',
    tytul: 'Import z krajów UE',
    opis: 'Niemcy, Holandia, Belgia, Dania + auta krajowe z pełną dokumentacją'
  }
];

// Szybkie filtry dla busów
export const szybkieFiltry = [
  { label: 'Do 3.5t', value: 'dmc_do_3_5t', count: 32 },
  { label: 'Z windą', value: 'z_winda', count: 18 },
  { label: 'Chłodnia', value: 'chlodnia', count: 12 },
  { label: 'L3H2', value: 'l3h2', count: 24 },
  { label: 'Brygadowy', value: 'brygadowy', count: 15 },
  { label: 'Euro 6', value: 'euro6', count: 38 },
  { label: '4×4', value: '4x4', count: 8 }
];

// Popularne marki dla mega-menu
export const popularneMarkiBusow = [
  { marka: 'Mercedes-Benz Sprinter', count: 12 },
  { marka: 'Ford Transit', count: 10 },
  { marka: 'Iveco Daily', count: 8 },
  { marka: 'Volkswagen Crafter', count: 7 },
  { marka: 'Renault Master', count: 6 },
  { marka: 'Peugeot Boxer', count: 5 }
];