import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
// Select components removed - using Input fields instead
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Star, 
  Eye, 
  BarChart3, 
  Users, 
  Truck,
  ArrowLeft,
  Save,
  X,
  RefreshCw
} from 'lucide-react';
import { generateDescription } from '../components/DescriptionGenerator';
// Mock data imports removed - using manual input instead

export const AdminPanel = () => {
  const navigate = useNavigate();
  const [buses, setBuses] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingBus, setEditingBus] = useState(null);
  const [newBus, setNewBus] = useState({
    marka: '',
    model: '',
    wersja: '',
    rok: new Date().getFullYear(),
    pierwszaRejestracja: '',
    przebieg: '',
    paliwo: '',
    skrzynia: '',
    naped: 'Przedni (FWD)',
    typNadwozia: '',
    dmc: '',
    ladownosc: '',
    kubatura: '',
    wymiarL: '',
    wymiarH: '',
    moc: '',
    pojemnosc: '',
    kolor: '',
    normaEmisji: '',
    adBlue: false,
    cenaBrutto: '',
    cenaNetto: '',
    vat: true,
    lokalizacja: '',
    gwarancja: true,
    wyrozniowane: false,
    nowosc: true,
    flotowy: false,
    // Podstawowe wyposażenie
    klimatyzacja: false,
    tempomat: false,
    czujniki_parkowania: false,
    kamera_cofania: false,
    webasto: false,
    podgrzewane_siedzenia: false,
    hak: false,
    elektryczne_szyby: false,
    elektryczne_lusterka: false,
    centralny_zamek: false,
    abs: false,
    alarm: false,
    asr: false,
    bluetooth: false,
    immobilizer: false,
    komputer_pokladowy: false,
    wielofunkcyjna_kierownica: false,
    nawigacja_gps: false,
    radio: false,
    poduszka_kierowcy: false,
    poduszka_pasazera: false,
    przesuwane_drzwi: false,
    tylne_drzwi_skrzydla: false,
    klapa_bagażnika: false,
    drzwi_tylne_360: false,
    wspomaganie_kierownicy: false,
    fotel_pneumatyczny: false,
    halogeny: false,
    oswietlenie_bagażowe: false,
    // Wyposażenie specjalistyczne LCV
    winda: false,
    klimatyzacja_ladunkowa: false,
    przegroda: false,
    twin_wheel: false,
    czterykola: false,
    drzwi: '',
    // Wymiary paki (mm)
    cargo_len_mm: '',
    cargo_w_mm: '',
    cargo_w_between_wheels_mm: '',
    cargo_h_mm: '',
    // Dodatkowe pola dla generatora
    seats: '',
    pierwszaRejestracja: '',
    invoice_type: 'VAT 23%', // "VAT 23%" | "VAT marża" | "VAT od faktury"
    financing: true,
    accident_free: true,
    paint_original: true,
    service_history: 'pełna', // "pełna" | "częściowa" | null
    delivery_available: true,
    // Generator settings
    auto_generate_description: true,
    opis: ''
  });

  // Załaduj busy z localStorage lub użyj domyślnych
  useEffect(() => {
    const savedBuses = localStorage.getItem('adminBuses');
    if (savedBuses) {
      setBuses(JSON.parse(savedBuses));
    } else {
      // Załaduj początkowe 10 busów jako przykład
      const mockBuses = JSON.parse(localStorage.getItem('mockBuses') || '[]').slice(0, 10);
      setBuses(mockBuses);
      localStorage.setItem('adminBuses', JSON.stringify(mockBuses));
    }
  }, []);

  // Zapisz busy do localStorage przy każdej zmianie
  useEffect(() => {
    localStorage.setItem('adminBuses', JSON.stringify(buses));
  }, [buses]);

  const handleInputChange = (field, value) => {
    setNewBus(prev => {
      const updated = {
        ...prev,
        [field]: value
      };

      // Auto-uzupełnianie pól zależnych
      if (field === 'cenaBrutto' && value) {
        updated.cenaNetto = Math.floor(value * 0.81);
      }

      // Automatyczne generowanie opisu jeśli włączone
      if (updated.auto_generate_description && field !== 'opis') {
        updated.opis = generateDescription(updated);
      }

      return updated;
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const busData = {
      ...newBus,
      id: editingBus ? editingBus.id : Date.now(),
      numerOgloszenia: editingBus ? editingBus.numerOgloszenia : `FKBUS${String(Date.now()).slice(-5)}`,
      dataPublikacji: editingBus ? editingBus.dataPublikacji : new Date(),
      status: 'aktywne',
      zdjecia: [
        'https://customer-assets.emergentagent.com/job_premium-autosite/artifacts/x95quwic_525300848_122105401868956303_2895063514729956344_n.jpg'
      ],
      kontakt: {
        nazwa: 'FHU FRANKO – Autohandel BUSY/DOSTAWCZE',
        telefon: '+48 123 456 789',
        email: 'busy@fhufranko.pl',
        godziny: 'Pn-Pt: 8:00-18:00, Sb: 9:00-15:00'
      },
      wyposazenie: {
        'Bezpieczeństwo': ['ABS', 'ESP', 'Poduszki powietrzne'],
        'Użytkowe': [],
        'Komfort': ['Klimatyzacja kabiny', 'Elektr. szyby', 'Centralny zamek']
      }
    };

    if (editingBus) {
      setBuses(prev => prev.map(bus => bus.id === editingBus.id ? busData : bus));
    } else {
      setBuses(prev => [...prev, busData]);
    }

    // Reset formularza
    setNewBus({
      marka: '',
      model: '',
      wersja: '',
      rok: new Date().getFullYear(),
      pierwszaRejestracja: '',
      przebieg: '',
      paliwo: '',
      skrzynia: '',
      naped: 'Przedni (FWD)',
      typNadwozia: '',
      dmc: '',
      ladownosc: '',
      kubatura: '',
      wymiarL: '',
      wymiarH: '',
      moc: '',
      pojemnosc: '',
      kolor: '',
      normaEmisji: '',
      adBlue: false,
      cenaBrutto: '',
      cenaNetto: '',
      vat: true,
      lokalizacja: '',
      gwarancja: true,
      wyrozniowane: false,
      nowosc: true,
      flotowy: false,
      // Podstawowe wyposażenie
      klimatyzacja: false,
      tempomat: false,
      czujniki_parkowania: false,
      kamera_cofania: false,
      webasto: false,
      podgrzewane_siedzenia: false,
      hak: false,
      elektryczne_szyby: false,
      elektryczne_lusterka: false,
      centralny_zamek: false,
      abs: false,
      alarm: false,
      asr: false,
      bluetooth: false,
      immobilizer: false,
      komputer_pokladowy: false,
      wielofunkcyjna_kierownica: false,
      nawigacja_gps: false,
      radio: false,
      poduszka_kierowcy: false,
      poduszka_pasazera: false,
      przesuwane_drzwi: false,
      tylne_drzwi_skrzydla: false,
      klapa_bagażnika: false,
      drzwi_tylne_360: false,
      wspomaganie_kierownicy: false,
      fotel_pneumatyczny: false,
      halogeny: false,
      oswietlenie_bagażowe: false,
      // Wyposażenie specjalistyczne LCV
      winda: false,
      klimatyzacja_ladunkowa: false,
      przegroda: false,
      twin_wheel: false,
      czterykola: false,
      drzwi: '',
      // Wymiary paki (mm)
      cargo_len_mm: '',
      cargo_w_mm: '',
      cargo_w_between_wheels_mm: '',
      cargo_h_mm: '',
      // Dodatkowe pola dla generatora
      seats: '',
      pierwszaRejestracja: '',
      invoice_type: 'VAT 23%',
      financing: true,
      accident_free: true,
      paint_original: true,
      service_history: 'pełna',
      delivery_available: true,
      // Generator settings
      auto_generate_description: true,
      opis: ''
    });
    setShowAddForm(false);
    setEditingBus(null);
  };

  const handleEdit = (bus) => {
    setEditingBus(bus);
    setNewBus(bus);
    setShowAddForm(true);
  };

  const handleDelete = (busId) => {
    if (window.confirm('Czy na pewno chcesz usunąć to ogłoszenie?')) {
      setBuses(prev => prev.filter(bus => bus.id !== busId));
    }
  };

  const toggleFeatured = (busId) => {
    setBuses(prev => prev.map(bus => 
      bus.id === busId ? { ...bus, wyrozniowane: !bus.wyrozniowane } : bus
    ));
  };

  const getStats = () => {
    return {
      total: buses.length,
      featured: buses.filter(bus => bus.wyrozniowane).length,
      new: buses.filter(bus => bus.nowosc).length,
      fleet: buses.filter(bus => bus.flotowy).length
    };
  };

  const stats = getStats();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Powrót do strony
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Panel Admina</h1>
              <p className="text-gray-600">Zarządzanie ogłoszeniami busów FHU FRANKO</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Badge variant="outline" className="text-sm">
              👤 Administrator
            </Badge>
          </div>
        </div>
      </div>

      <div className="p-6">
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
            <TabsTrigger value="dashboard" className="flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="buses" className="flex items-center">
              <Truck className="h-4 w-4 mr-2" />
              Ogłoszenia
            </TabsTrigger>
            <TabsTrigger value="add" className="flex items-center">
              <Plus className="h-4 w-4 mr-2" />
              Dodaj Bus
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Użytkownicy
            </TabsTrigger>
          </TabsList>

          {/* Dashboard */}
          <TabsContent value="dashboard">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-full">
                      <Truck className="h-6 w-6 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Wszystkie busy</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-yellow-100 rounded-full">
                      <Star className="h-6 w-6 text-yellow-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Wyróżnione</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.featured}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-full">
                      <Plus className="h-6 w-6 text-green-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Nowe</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.new}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-purple-100 rounded-full">
                      <Eye className="h-6 w-6 text-purple-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Flotowe</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.fleet}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Lista Ogłoszeń */}
          <TabsContent value="buses">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Zarządzanie ogłoszeniami busów</CardTitle>
                  <Button
                    onClick={() => setShowAddForm(true)}
                    className="bg-[#F3BC30] hover:bg-[#E0AA2B] text-[#222122]"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Dodaj nowe ogłoszenie
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {buses.map((bus) => (
                    <div key={bus.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h3 className="font-semibold text-lg">
                            {bus.marka} {bus.model}
                          </h3>
                          <Badge variant="outline">{bus.typNadwozia}</Badge>
                          {bus.wyrozniowane && <Badge className="bg-[#F3BC30] text-[#222122]">Wyróżnione</Badge>}
                          {bus.nowosc && <Badge variant="secondary" className="bg-green-100 text-green-800">Nowość</Badge>}
                        </div>
                        <div className="mt-1 text-sm text-gray-600">
                          {bus.rok} • {bus.przebieg?.toLocaleString()} km • {bus.cenaBrutto?.toLocaleString()} zł • {bus.lokalizacja}
                        </div>
                        <div className="mt-1 text-xs text-gray-500">
                          Nr: {bus.numerOgloszenia} • DMC: {bus.dmc} kg • Ładowność: {bus.ladownosc} kg
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleFeatured(bus.id)}
                          className={bus.wyrozniowane ? 'text-yellow-600' : 'text-gray-400'}
                        >
                          <Star className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(bus)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(bus.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {buses.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Truck className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Brak ogłoszeń busów</p>
                      <p className="text-sm">Dodaj pierwsze ogłoszenie używając przycisku powyżej</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Formularz Dodawania */}
          <TabsContent value="add">
            <Card>
              <CardHeader>
                <CardTitle>
                  {editingBus ? 'Edytuj ogłoszenie busa' : 'Dodaj nowe ogłoszenie busa'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Podstawowe informacje */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="marka">Marka *</Label>
                      <Input
                        id="marka"
                        value={newBus.marka}
                        onChange={(e) => handleInputChange('marka', e.target.value)}
                        placeholder="np. Ford, Renault, Mercedes"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="model">Model *</Label>
                      <Input
                        id="model"
                        value={newBus.model}
                        onChange={(e) => handleInputChange('model', e.target.value)}
                        placeholder="np. Transit, Master, Sprinter"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="wersja">Wersja</Label>
                      <Input
                        value={newBus.wersja}
                        onChange={(e) => handleInputChange('wersja', e.target.value)}
                        placeholder="np. 2.0 TDI"
                      />
                    </div>
                  </div>

                  {/* Typ nadwozia i rok */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="typNadwozia">Typ nadwozia *</Label>
                      <Input
                        id="typNadwozia"
                        value={newBus.typNadwozia}
                        onChange={(e) => handleInputChange('typNadwozia', e.target.value)}
                        placeholder="np. Furgon, Kontener, Plandeka"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="rok">Rok produkcji *</Label>
                      <Input
                        type="number"
                        value={newBus.rok}
                        onChange={(e) => handleInputChange('rok', parseInt(e.target.value))}
                        min="2000"
                        max={new Date().getFullYear() + 1}
                        required
                      />
                    </div>
                  </div>

                  {/* Parametry LCV */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <Label htmlFor="dmc">DMC (kg) *</Label>
                      <Input
                        type="number"
                        value={newBus.dmc}
                        onChange={(e) => handleInputChange('dmc', parseInt(e.target.value))}
                        placeholder="3500"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="ladownosc">Ładowność (kg) *</Label>
                      <Input
                        type="number"
                        value={newBus.ladownosc}
                        onChange={(e) => handleInputChange('ladownosc', parseInt(e.target.value))}
                        placeholder="1400"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="wymiarL">Długość</Label>
                      <Input
                        id="wymiarL"
                        value={newBus.wymiarL}
                        onChange={(e) => handleInputChange('wymiarL', e.target.value)}
                        placeholder="np. L1, L2, L3, L4"
                      />
                    </div>

                    <div>
                      <Label htmlFor="wymiarH">Wysokość</Label>
                      <Input
                        id="wymiarH"
                        value={newBus.wymiarH}
                        onChange={(e) => handleInputChange('wymiarH', e.target.value)}
                        placeholder="np. H1, H2, H3"
                      />
                    </div>
                  </div>

                  {/* Cena */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="cenaBrutto">Cena brutto (PLN) *</Label>
                      <Input
                        type="number"
                        value={newBus.cenaBrutto}
                        onChange={(e) => handleInputChange('cenaBrutto', parseInt(e.target.value))}
                        placeholder="50000"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="cenaNetto">Cena netto (PLN)</Label>
                      <Input
                        type="number"
                        value={newBus.cenaNetto}
                        readOnly
                        className="bg-gray-50"
                      />
                    </div>
                  </div>

                  {/* Wymiary paki */}
                  <div>
                    <Label>Wymiary paki (mm) - opcjonalne</Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
                      <div>
                        <Label htmlFor="cargo_len_mm">Długość [mm]</Label>
                        <Input
                          id="cargo_len_mm"
                          type="number"
                          value={newBus.cargo_len_mm}
                          onChange={(e) => handleInputChange('cargo_len_mm', e.target.value)}
                          placeholder="np. 3200"
                        />
                      </div>
                      <div>
                        <Label htmlFor="cargo_w_mm">Szerokość [mm]</Label>
                        <Input
                          id="cargo_w_mm"
                          type="number"
                          value={newBus.cargo_w_mm}
                          onChange={(e) => handleInputChange('cargo_w_mm', e.target.value)}
                          placeholder="np. 1700"
                        />
                      </div>
                      <div>
                        <Label htmlFor="cargo_w_between_wheels_mm">Szerokość między nadkolami [mm]</Label>  
                        <Input
                          id="cargo_w_between_wheels_mm"
                          type="number"
                          value={newBus.cargo_w_between_wheels_mm}
                          onChange={(e) => handleInputChange('cargo_w_between_wheels_mm', e.target.value)}
                          placeholder="np. 1250"
                        />
                      </div>
                      <div>
                        <Label htmlFor="cargo_h_mm">Wysokość [mm]</Label>
                        <Input
                          id="cargo_h_mm"
                          type="number"
                          value={newBus.cargo_h_mm}
                          onChange={(e) => handleInputChange('cargo_h_mm', e.target.value)}
                          placeholder="np. 1900"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Dodatkowe informacje */}
                  <div>
                    <Label>Dodatkowe informacje</Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
                      <div>
                        <Label htmlFor="seats">Liczba miejsc</Label>
                        <Input
                          id="seats"
                          type="number"
                          value={newBus.seats}
                          onChange={(e) => handleInputChange('seats', e.target.value)}
                          placeholder="np. 3"
                        />
                      </div>
                      <div>
                        <Label htmlFor="pierwszaRejestracja">Data I rejestracji</Label>
                        <Input
                          id="pierwszaRejestracja"
                          type="date"
                          value={newBus.pierwszaRejestracja}
                          onChange={(e) => handleInputChange('pierwszaRejestracja', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label htmlFor="invoice_type">Typ faktury</Label>
                        <select
                          id="invoice_type"
                          value={newBus.invoice_type}
                          onChange={(e) => handleInputChange('invoice_type', e.target.value)}
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        >
                          <option value="VAT 23%">VAT 23%</option>
                          <option value="VAT marża">VAT marża</option>
                          <option value="VAT od faktury">VAT od faktury</option>
                        </select>
                      </div>
                      <div>
                        <Label htmlFor="service_history">Historia serwisowa</Label>
                        <select
                          id="service_history"
                          value={newBus.service_history}
                          onChange={(e) => handleInputChange('service_history', e.target.value)}
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        >
                          <option value="pełna">Pełna</option>
                          <option value="częściowa">Częściowa</option>
                          <option value="">Brak</option>
                        </select>
                      </div>
                    </div>
                    
                    {/* Checkboxy dla flagg */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={newBus.financing}
                          onChange={(e) => handleInputChange('financing', e.target.checked)}
                        />
                        <span>Możliwość finansowania</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={newBus.accident_free}
                          onChange={(e) => handleInputChange('accident_free', e.target.checked)}
                        />
                        <span>Bezwypadkowy</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={newBus.paint_original}
                          onChange={(e) => handleInputChange('paint_original', e.target.checked)}
                        />
                        <span>Oryginalny lakier</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={newBus.delivery_available}
                          onChange={(e) => handleInputChange('delivery_available', e.target.checked)}
                        />
                        <span>Dostawa pod dom</span>
                      </label>
                    </div>
                  </div>

                  {/* Checkboxy wyposażenia */}
                  <div>
                    <Label>Wyposażenie użytkowe</Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mt-2 max-h-64 overflow-y-auto border rounded p-4">
                      {[
                        { key: 'klimatyzacja', label: 'Klimatyzacja' },
                        { key: 'tempomat', label: 'Tempomat' },
                        { key: 'czujniki_parkowania', label: 'Czujniki parkowania' },
                        { key: 'kamera_cofania', label: 'Kamera cofania' },
                        { key: 'webasto', label: 'Webasto' },
                        { key: 'podgrzewane_siedzenia', label: 'Podgrzewane siedzenia' },
                        { key: 'hak', label: 'Hak' },
                        { key: 'elektryczne_szyby', label: 'Elektryczne szyby' },
                        { key: 'elektryczne_lusterka', label: 'Elektryczne lusterka' },
                        { key: 'centralny_zamek', label: 'Centralny zamek' },
                        { key: 'abs', label: 'ABS' },
                        { key: 'alarm', label: 'Alarm' },
                        { key: 'asr', label: 'ASR' },
                        { key: 'bluetooth', label: 'Bluetooth' },
                        { key: 'immobilizer', label: 'Immobilizer' },
                        { key: 'komputer_pokladowy', label: 'Komputer pokładowy' },
                        { key: 'wielofunkcyjna_kierownica', label: 'Wielofunkcyjna kierownica' },
                        { key: 'nawigacja_gps', label: 'Nawigacja GPS' },
                        { key: 'radio', label: 'Radio' },
                        { key: 'poduszka_kierowcy', label: 'Poduszka powietrzna kierowcy' },
                        { key: 'poduszka_pasazera', label: 'Poduszka powietrzna pasażera' },
                        { key: 'przesuwane_drzwi', label: 'Przesuwane drzwi' },
                        { key: 'tylne_drzwi_skrzydla', label: 'Tylne drzwi skrzydełka' },
                        { key: 'klapa_bagażnika', label: 'Klapa bagażnika' },
                        { key: 'drzwi_tylne_360', label: 'Drzwi tylne 360°' },
                        { key: 'wspomaganie_kierownicy', label: 'Wspomaganie kierownicy' },
                        { key: 'fotel_pneumatyczny', label: 'Fotel pneumatyczny' },
                        { key: 'halogeny', label: 'Halogeny' },
                        { key: 'oswietlenie_bagażowe', label: 'Oświetlenie przestrzeni bagażowej' },
                        // Dodatkowe opcje specyficzne dla LCV
                        { key: 'winda', label: 'Winda załadowcza' },
                        { key: 'klimatyzacja_ladunkowa', label: 'Klimatyzacja ładunkowa' },  
                        { key: 'przegroda', label: 'Przegroda kabiny' },
                        { key: 'twin_wheel', label: 'Twin wheel (bliźniaki)' },
                        { key: 'czterykola', label: '4×4' },
                        { key: 'wyrozniowane', label: 'Wyróżnione' },
                        { key: 'flotowy', label: 'Flotowy' }
                      ].map(item => (
                        <label key={item.key} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newBus[item.key]}
                            onChange={(e) => handleInputChange(item.key, e.target.checked)}
                            className="rounded border-gray-300"
                          />
                          <span className="text-sm">{item.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Generator opisu */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label htmlFor="opis">Opis ogłoszenia</Label>
                      <div className="flex items-center space-x-4">
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newBus.auto_generate_description}
                            onChange={(e) => handleInputChange('auto_generate_description', e.target.checked)}
                          />
                          <span className="text-sm">Generuj opis automatycznie</span>
                        </label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={!newBus.auto_generate_description}
                          onClick={() => {
                            const generatedDescription = generateDescription(newBus);
                            handleInputChange('opis', generatedDescription);
                          }}
                        >
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Odśwież opis
                        </Button>
                      </div>
                    </div>
                    <Textarea
                      value={newBus.opis}
                      onChange={(e) => handleInputChange('opis', e.target.value)}
                      placeholder="Opis będzie wygenerowany automatycznie na podstawie wypełnionych pól..."
                      rows={8}
                      className="font-mono text-sm"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      💡 Opis jest generowany automatycznie z wypełnionych pól formularza. 
                      {!newBus.auto_generate_description && " Odznacz checkbox aby edytować ręcznie."}
                    </p>
                  </div>

                  {/* Przyciski */}
                  <div className="flex justify-end space-x-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowAddForm(false);
                        setEditingBus(null);
                      }}
                    >
                      <X className="h-4 w-4 mr-2" />
                      Anuluj
                    </Button>
                    <Button
                      type="submit"
                      className="bg-[#F3BC30] hover:bg-[#E0AA2B] text-[#222122]"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      {editingBus ? 'Zapisz zmiany' : 'Dodaj ogłoszenie'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Użytkownicy (mockowy) */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>Zarządzanie użytkownikami</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Funkcja w przygotowaniu</p>
                  <p className="text-sm">Zarządzanie użytkownikami będzie dostępne wkrótce</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};