// Autogenerator opisów ogłoszeń dla BUSY/DOSTAWCZE
// Implementuje silnik szablonów podobny do Handlebars

// Mapowanie wyposażenia do kategorii
const EQUIPMENT_CATEGORIES = {
  'Bezpieczeństwo/układy': [
    'abs', 'asr', 'esp', 'alarm', 'immobilizer', 
    'poduszka_kierowcy', 'poduszka_pasazera'
  ],
  'Komfort/sterowanie': [
    'klimatyzacja', 'webasto', 'podgrzewane_siedzenia', 
    'elektryczne_szyby', 'elektryczne_lusterka', 'centralny_zamek',
    'wspomaganie_kierownicy', 'fotel_pneumatyczny', 'komputer_pokladowy',
    'klimatyzacja_ladunkowa'
  ],
  'Asysta/infotainment': [
    'tempomat', 'czujniki_parkowania', 'kamera_cofania', 
    'nawigacja_gps', 'radio', 'bluetooth', 'wielofunkcyjna_kierownica'
  ],
  'Nadwozie/dostęp': [
    'przesuwane_drzwi', 'tylne_drzwi_skrzydla', 'drzwi_tylne_360',
    'klapa_bagażnika', 'halogeny', 'oswietlenie_bagażowe',
    'winda', 'przegroda', 'twin_wheel'
  ]
};

// Mapowanie nazw pól do czytelnych etykiet
const EQUIPMENT_LABELS = {
  'abs': 'ABS',
  'asr': 'ASR', 
  'esp': 'ESP',
  'alarm': 'Alarm',
  'immobilizer': 'Immobilizer',
  'poduszka_kierowcy': 'Poduszka powietrzna kierowcy',
  'poduszka_pasazera': 'Poduszka powietrzna pasażera',
  'klimatyzacja': 'Klimatyzacja',
  'webasto': 'Webasto',
  'podgrzewane_siedzenia': 'Podgrzewane siedzenia',
  'elektryczne_szyby': 'Elektryczne szyby',
  'elektryczne_lusterka': 'Elektryczne lusterka',
  'centralny_zamek': 'Centralny zamek',
  'wspomaganie_kierownicy': 'Wspomaganie kierownicy',
  'fotel_pneumatyczny': 'Fotel pneumatyczny',
  'komputer_pokladowy': 'Komputer pokładowy',
  'klimatyzacja_ladunkowa': 'Klimatyzacja ładunkowa',
  'tempomat': 'Tempomat',
  'czujniki_parkowania': 'Czujniki parkowania',
  'kamera_cofania': 'Kamera cofania',
  'nawigacja_gps': 'Nawigacja GPS',
  'radio': 'Radio',
  'bluetooth': 'Bluetooth',
  'wielofunkcyjna_kierownica': 'Wielofunkcyjna kierownica',
  'przesuwane_drzwi': 'Przesuwane drzwi',
  'tylne_drzwi_skrzydla': 'Tylne drzwi skrzydełka',
  'drzwi_tylne_360': 'Drzwi tylne 360°',
  'klapa_bagażnika': 'Klapa bagażnika',
  'halogeny': 'Halogeny',
  'oswietlenie_bagażowe': 'Oświetlenie przestrzeni bagażowej',
  'winda': 'Winda załadowcza',
  'przegroda': 'Przegroda kabiny',
  'twin_wheel': 'Twin wheel (bliźniaki)',
  'hak': 'Hak',
  'czterykola': '4x4'
};

// Domyślny szablon opisu
const DEFAULT_TEMPLATE = `Witam, przedmiotem sprzedaży jest:

{{marka}} {{model}}{{#if wersja}} {{wersja}}{{/if}}{{#if wymiarL}}{{#if wymiarH}} {{wymiarL}}{{wymiarH}}{{/if}}{{/if}}
{{#if typNadwozia}}{{typNadwozia}}{{/if}}{{#if seats}} {{seats}}-osobowy{{/if}}

{{#if pierwszaRejestracja}}Data I rej.: {{pierwszaRejestracja}}.{{/if}}

Polub nasz profil na Facebooku, aby być na bieżąco z ofertami aut dostawczych:
https://www.facebook.com/profile.php?id=61578689111557

{{#if delivery_available}}*** MOŻLIWOŚĆ DOSTARCZENIA AUTA POD DOM ***{{/if}}

# AUTO W BARDZO DOBRYM STANIE TECHNICZNYM I WIZUALNYM{{#if accident_free}}!{{/if}}
{{#if przebieg}}# Przebieg {{formatNumber przebieg}} km{{#if service_history}}, {{#if (eq service_history "pełna")}}serwisowany od początku – gwarancja przebiegu{{else}}udokumentowany serwis{{/if}}{{/if}}.{{/if}}
# Samochód bez wkładu finansowego. 
{{#if accident_free}}# Bezwypadkowy.{{/if}} {{#if paint_original}}Wszystkie szyby i lakier w oryginale.{{/if}}
{{#if invoice_type}}# {{#if (eq invoice_type "VAT 23%")}}Faktura VAT 23%{{/if}}{{#if (eq invoice_type "VAT marża")}}Faktura VAT Marża{{/if}}{{#if (eq invoice_type "VAT od faktury")}}VAT od faktury{{/if}}.{{/if}}
{{#if financing}}# Możliwość finansowania: Leasing / Kredyt / Raty.{{/if}}

{{#if (or cargo_len_mm cargo_w_mm cargo_w_between_wheels_mm cargo_h_mm)}}
Wymiary paki (mm):
{{#if cargo_len_mm}}- Długość: {{cargo_len_mm}} mm{{/if}}
{{#if cargo_w_mm}}- Szerokość: {{cargo_w_mm}} mm{{/if}}
{{#if cargo_w_between_wheels_mm}}- Szerokość między nadkolami: {{cargo_w_between_wheels_mm}} mm{{/if}}
{{#if cargo_h_mm}}- Wysokość: {{cargo_h_mm}} mm{{/if}}
{{/if}}

WYPOSAŻENIE:
{{#if (anyIn equipment "Bezpieczeństwo/układy")}}
- **Bezpieczeństwo/układy:** {{listCategory equipment "Bezpieczeństwo/układy"}}
{{/if}}
{{#if (anyIn equipment "Komfort/sterowanie")}}
- **Komfort/sterowanie:** {{listCategory equipment "Komfort/sterowanie"}}
{{/if}}
{{#if (anyIn equipment "Asysta/infotainment")}}
- **Asysta/infotainment:** {{listCategory equipment "Asysta/infotainment"}}
{{/if}}
{{#if (anyIn equipment "Nadwozie/dostęp")}}
- **Nadwozie/dostęp:** {{listCategory equipment "Nadwozie/dostęp"}}
{{/if}}
{{#if (hasFlag equipment "hak")}}
- **Hak**
{{/if}}
{{#if (hasFlag equipment "czterykola")}}
- **Napęd 4x4**
{{/if}}

Więcej informacji pod nr tel.: Wyświetl numer

*** ZAPRASZAM! ***

Niniejsze ogłoszenie jest wyłącznie informacją handlową i stanowi zaproszenie do zawarcia umowy (art. 71 Kodeksu cywilnego); nie stanowi natomiast oferty handlowej w rozumieniu art. 66 § 1 KC i następnych. W celu weryfikacji zgodności oferty prosimy o kontakt z przedstawicielem firmy.`;

// Helpery szablonu
const formatNumber = (num) => {
  if (!num) return '';
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
};

const eq = (a, b) => a === b;

const anyIn = (equipment, category) => {
  if (!equipment || !EQUIPMENT_CATEGORIES[category]) return false;
  return EQUIPMENT_CATEGORIES[category].some(key => equipment[key] === true);
};

const listCategory = (equipment, category) => {
  if (!equipment || !EQUIPMENT_CATEGORIES[category]) return '';
  
  const items = EQUIPMENT_CATEGORIES[category]
    .filter(key => equipment[key] === true)
    .map(key => EQUIPMENT_LABELS[key] || key)
    .filter(Boolean);
    
  return items.join(', ');
};

const hasFlag = (equipment, flag) => {
  return equipment && equipment[flag] === true;
};

// Prostszy parser szablonów (zamiast pełnego Handlebars)
const parseTemplate = (template, data) => {
  let result = template;
  
  // Helper functions map
  const helpers = { formatNumber, eq, anyIn, listCategory, hasFlag };
  
  // Simple variable substitution {{variable}}
  result = result.replace(/\{\{([^}#\/]+)\}\}/g, (match, variable) => {
    const trimmed = variable.trim();
    
    // Handle helper functions
    if (trimmed.includes(' ')) {
      const parts = trimmed.split(' ');
      const helperName = parts[0];
      
      if (helpers[helperName]) {
        const args = parts.slice(1).map(arg => {
          if (arg.startsWith('"') && arg.endsWith('"')) {
            return arg.slice(1, -1); // Remove quotes
          }
          return data[arg] || arg;
        });
        
        const result = helpers[helperName](...args);
        return result || '';
      }
    }
    
    return data[trimmed] || '';
  });
  
  // Handle {{#if condition}}...{{/if}}
  result = result.replace(/\{\{#if\s+([^}]+)\}\}([\s\S]*?)\{\{\/if\}\}/g, (match, condition, content) => {
    let conditionResult = false;
    
    // Handle helper conditions like (eq service_history "pełna")
    if (condition.includes('(') && condition.includes(')')) {
      const helperMatch = condition.match(/\((\w+)\s+([^)]+)\)/);
      if (helperMatch) {
        const [, helperName, args] = helperMatch;
        if (helpers[helperName]) {
          const argList = args.split(' ').map(arg => {
            if (arg.startsWith('"') && arg.endsWith('"')) {
              return arg.slice(1, -1);
            }
            return data[arg] || arg;
          });
          conditionResult = helpers[helperName](...argList);
        }
      }
    } else if (condition.includes('(or')) {
      // Handle (or field1 field2 field3)
      const orMatch = condition.match(/\(or\s+([^)]+)\)/);
      if (orMatch) {
        const fields = orMatch[1].split(' ');
        conditionResult = fields.some(field => data[field.trim()]);
      }
    } else {
      // Simple condition
      conditionResult = !!data[condition.trim()];
    }
    
    return conditionResult ? content : '';
  });
  
  // Clean up extra whitespace
  result = result.replace(/\n\s*\n\s*\n/g, '\n\n');
  
  return result;
};

// Główna funkcja generatora
export const generateDescription = (vehicle, template = DEFAULT_TEMPLATE) => {
  // Prepare equipment object for template
  const equipment = {};
  
  // Map vehicle properties to equipment object
  Object.keys(vehicle).forEach(key => {
    if (key.includes('_') || ['hak', 'czterykola'].includes(key)) {
      equipment[key] = vehicle[key];
    }
  });
  
  // Prepare data for template
  const templateData = {
    ...vehicle,
    equipment,
    formatNumber: (num) => formatNumber(num),
    eq: (a, b) => eq(a, b),
    anyIn: (eq, cat) => anyIn(equipment, cat),
    listCategory: (eq, cat) => listCategory(equipment, cat),
    hasFlag: (eq, flag) => hasFlag(equipment, flag)
  };
  
  return parseTemplate(template, templateData);
};

export { DEFAULT_TEMPLATE, EQUIPMENT_CATEGORIES, EQUIPMENT_LABELS };