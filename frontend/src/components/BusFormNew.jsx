import React, { useState, useEffect, useMemo } from 'react';
import ReactQuill from 'react-quill';
import DatePicker, { registerLocale } from 'react-datepicker';
import pl from 'date-fns/locale/pl';
import 'react-quill/dist/quill.snow.css';
import 'react-datepicker/dist/react-datepicker.css';
import { marki, modele, paliwa, skrzynie, typyNadwozi, normyEmisji, dmcKategorie, kolory, krajePochodzenia, stany } from '../constants/formOptions';
import * as busApi from '../api/busApi';
import { toast } from 'sonner';

// Register Polish locale for date picker
registerLocale('pl', pl);

/**
 * New Listing Form Component - 4 Sections
 * Sekcja 1: Informacje podstawowe
 * Sekcja 2: Specyfikacja techniczna
 * Sekcja 3: Stan i historia pojazdu
 * Sekcja 4: Opis sprzedawcy
 */
const BusFormNew = ({ editData, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState(1);
  const [errors, setErrors] = useState({});
  
  // Otomoto import
  const [otomotoUrl, setOtomotoUrl] = useState('');
  const [importing, setImporting] = useState(false);

  // ========== SEKCJA 1: Informacje podstawowe ==========
  const [title, setTitle] = useState('');
  const [pricePln, setPricePln] = useState('');
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [color, setColor] = useState('');
  const [seats, setSeats] = useState('');
  const [productionYear, setProductionYear] = useState('');
  const [vin, setVin] = useState('');
  const [installmentsAvailable, setInstallmentsAvailable] = useState(false);

  // ========== SEKCJA 2: Specyfikacja techniczna ==========
  const [fuelType, setFuelType] = useState('Diesel');
  const [engineDisplacementCc, setEngineDisplacementCc] = useState('');
  const [powerHp, setPowerHp] = useState('');
  const [bodyType, setBodyType] = useState('');
  const [gearbox, setGearbox] = useState('Manualna');
  const [gvwKg, setGvwKg] = useState('');
  const [twinRearWheels, setTwinRearWheels] = useState(false);

  // ========== SEKCJA 3: Stan i historia pojazdu ==========
  const [originCountry, setOriginCountry] = useState('');
  const [mileageKm, setMileageKm] = useState('');
  const [registrationNumber, setRegistrationNumber] = useState('');
  const [conditionStatus, setConditionStatus] = useState('Używany');
  const [firstRegistrationDate, setFirstRegistrationDate] = useState(null);
  const [accidentFree, setAccidentFree] = useState(false);
  const [hasRegistrationNumber, setHasRegistrationNumber] = useState(false);
  const [servicedInAso, setServicedInAso] = useState(false);

  // ========== SEKCJA 4: Opis sprzedawcy ==========
  const [descriptionHtml, setDescriptionHtml] = useState('');
  const [homeDelivery, setHomeDelivery] = useState(false);
  const [techVisualShort, setTechVisualShort] = useState('');
  const [sellerProfileUrl, setSellerProfileUrl] = useState('');
  const [locationStreet, setLocationStreet] = useState('');
  const [locationCity, setLocationCity] = useState('Smyków');
  const [locationRegion, setLocationRegion] = useState('Świętokrzyskie');

  // Additional fields
  const [zdjecia, setZdjecia] = useState([]);
  const [zdjecieGlowne, setZdjecieGlowne] = useState('');
  const [wyrozniowane, setWyrozniowane] = useState(false);
  const [nowosc, setNowosc] = useState(false);
  const [flotowy, setFlotowy] = useState(false);
  const [gwarancja, setGwarancja] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);

  // Auto-generate title when make/model change
  useEffect(() => {
    if (make && model) {
      setTitle(`${make} ${model}`);
    }
  }, [make, model]);

  // Load edit data
  useEffect(() => {
    if (editData) {
      // Map old field names to new ones
      setTitle(editData.title || `${editData.marka} ${editData.model}`);
      setPricePln(editData.cenaBrutto || editData.price_pln || '');
      setMake(editData.marka || editData.make || '');
      setModel(editData.model || '');
      setColor(editData.color || editData.kolor || '');
      setSeats(editData.liczbaMiejsc || editData.seats || '');
      setProductionYear(editData.rok || editData.production_year || '');
      setVin(editData.vin || '');
      setInstallmentsAvailable(editData.installments_available || false);
      
      setFuelType(editData.paliwo || editData.fuel_type || 'Diesel');
      setEngineDisplacementCc(editData.kubatura || editData.engine_displacement_cc || '');
      setPowerHp(editData.moc || editData.power_hp || '');
      setBodyType(editData.typNadwozia || editData.body_type || '');
      setGearbox(editData.skrzynia || editData.gearbox || 'Manualna');
      setGvwKg(editData.gvw_kg || '');
      setTwinRearWheels(editData.twin_rear_wheels || false);
      
      setOriginCountry(editData.origin_country || editData.krajPochodzenia || '');
      setMileageKm(editData.przebieg || editData.mileage_km || '');
      setRegistrationNumber(editData.registration_number || editData.numerRejestracyjny || '');
      setConditionStatus(editData.condition_status || editData.stan || 'Używany');
      if (editData.first_registration_date || editData.dataPierwszejRejestracji) {
        setFirstRegistrationDate(new Date(editData.first_registration_date || editData.dataPierwszejRejestracji));
      }
      setAccidentFree(editData.accident_free || editData.bezwypadkowy || false);
      setHasRegistrationNumber(editData.has_registration_number || editData.maNumerRejestracyjny || false);
      setServicedInAso(editData.serviced_in_aso || editData.serwisowanyWAso || false);
      
      setDescriptionHtml(editData.description_html || editData.opis || '');
      setHomeDelivery(editData.home_delivery || false);
      setTechVisualShort(editData.tech_visual_short || '');
      setSellerProfileUrl(editData.seller_profile_url || '');
      setLocationStreet(editData.location_street || '');
      setLocationCity(editData.location_city || 'Smyków');
      setLocationRegion(editData.location_region || 'Świętokrzyskie');
      
      setZdjecia(editData.zdjecia || []);
      setZdjecieGlowne(editData.zdjecieGlowne || '');
      setWyrozniowane(editData.wyrozniowane || false);
      setNowosc(editData.nowosc || false);
      setFlotowy(editData.flotowy || false);
      setGwarancja(editData.gwarancja || false);
    }
  }, [editData]);

  // Import from Otomoto
  const handleOtomotoImport = async () => {
    if (!otomotoUrl.trim()) {
      toast.error('Podaj URL ogłoszenia Otomoto');
      return;
    }

    setImporting(true);
    try {
      const result = await busApi.scrapeOtomoto(otomotoUrl);
      
      if (result.success && result.data) {
        const data = result.data;
        
        // Map scraped data to new fields
        if (data.marka) setMake(data.marka);
        if (data.model) setModel(data.model);
        if (data.cenaBrutto) setPricePln(data.cenaBrutto);
        if (data.rok) setProductionYear(data.rok);
        if (data.przebieg) setMileageKm(data.przebieg);
        if (data.paliwo) setFuelType(data.paliwo);
        if (data.skrzynia) setGearbox(data.skrzynia);
        if (data.moc) setPowerHp(data.moc);
        if (data.kubatura) setEngineDisplacementCc(data.kubatura);
        if (data.typNadwozia) setBodyType(data.typNadwozia);
        if (data.kolor) setColor(data.kolor);
        if (data.krajPochodzenia) setOriginCountry(data.krajPochodzenia);
        if (data.stan) setConditionStatus(data.stan);
        if (data.opis) setDescriptionHtml(data.opis);
        if (typeof data.bezwypadkowy === 'boolean') setAccidentFree(data.bezwypadkowy);
        
        toast.success('Dane zaimportowane z Otomoto! Sprawdź i uzupełnij brakujące pola.');
        
        if (result.missing_fields && result.missing_fields.length > 0) {
          console.log('Pola do uzupełnienia:', result.missing_fields);
        }
      }
    } catch (error) {
      toast.error(error.message || 'Błąd importu z Otomoto');
    } finally {
      setImporting(false);
    }
  };

  // Image upload
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingImage(true);
    try {
      const result = await busApi.uploadImage(file);
      if (result.success) {
        const newImages = [...zdjecia, result.url];
        setZdjecia(newImages);
        
        if (!zdjecieGlowne) {
          setZdjecieGlowne(result.url);
        }
        
        toast.success('Zdjęcie dodane');
      }
    } catch (error) {
      toast.error('Błąd przesyłania zdjęcia');
    } finally {
      setUploadingImage(false);
    }
  };

  const removeImage = (url) => {
    setZdjecia(zdjecia.filter(img => img !== url));
    if (zdjecieGlowne === url) {
      setZdjecieGlowne(zdjecia[0] || '');
    }
  };

  // Format number with spaces
  const formatNumber = (value) => {
    if (!value) return '';
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Required fields - Sekcja 1
    if (!title.trim()) newErrors.title = 'Tytuł jest wymagany';
    if (!pricePln || pricePln <= 0) newErrors.pricePln = 'Cena musi być większa od 0';
    if (!make) newErrors.make = 'Marka jest wymagana';
    if (!model) newErrors.model = 'Model jest wymagany';
    if (!productionYear || productionYear < 1950) newErrors.productionYear = 'Podaj prawidłowy rok produkcji';
    
    // VIN validation
    if (vin && vin.length !== 17) {
      newErrors.vin = 'VIN musi mieć dokładnie 17 znaków';
    }

    // Required fields - Sekcja 2
    if (!fuelType) newErrors.fuelType = 'Rodzaj paliwa jest wymagany';
    if (!bodyType) newErrors.bodyType = 'Typ nadwozia jest wymagany';
    if (!gearbox) newErrors.gearbox = 'Skrzynia biegów jest wymagana';

    // Required fields - Sekcja 3
    if (!mileageKm || mileageKm < 0) newErrors.mileageKm = 'Przebieg jest wymagany';
    if (!conditionStatus) newErrors.conditionStatus = 'Stan pojazdu jest wymagany';

    // Required fields - Sekcja 4
    if (!descriptionHtml || descriptionHtml.length < 20) newErrors.descriptionHtml = 'Opis musi mieć co najmniej 20 znaków';
    if (!locationCity) newErrors.locationCity = 'Miejscowość jest wymagana';
    if (!locationRegion) newErrors.locationRegion = 'Województwo jest wymagane';
    
    // URL validation
    if (sellerProfileUrl && !sellerProfileUrl.match(/^https?:\/\/.+/)) {
      newErrors.sellerProfileUrl = 'Podaj prawidłowy URL (http:// lub https://)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Uzupełnij wymagane pola');
      return;
    }

    setLoading(true);
    try {
      const listingData = {
        // Sekcja 1
        title,
        price_pln: parseInt(pricePln),
        make,
        model,
        color: color || null,
        seats: seats ? parseInt(seats) : null,
        production_year: parseInt(productionYear),
        vin: vin || null,
        installments_available: installmentsAvailable,
        
        // Sekcja 2
        fuel_type: fuelType,
        engine_displacement_cc: engineDisplacementCc ? parseInt(engineDisplacementCc) : null,
        power_hp: powerHp ? parseInt(powerHp) : null,
        body_type: bodyType,
        gearbox,
        gvw_kg: gvwKg ? parseInt(gvwKg) : null,
        twin_rear_wheels: twinRearWheels,
        
        // Sekcja 3
        origin_country: originCountry || null,
        mileage_km: parseInt(mileageKm),
        registration_number: registrationNumber || null,
        condition_status: conditionStatus,
        first_registration_date: firstRegistrationDate ? firstRegistrationDate.toISOString().split('T')[0] : null,
        accident_free: accidentFree,
        has_registration_number: hasRegistrationNumber,
        serviced_in_aso: servicedInAso,
        
        // Sekcja 4
        description_html: descriptionHtml,
        home_delivery: homeDelivery,
        tech_visual_short: techVisualShort || null,
        seller_profile_url: sellerProfileUrl || null,
        location_street: locationStreet || null,
        location_city: locationCity,
        location_region: locationRegion,
        
        // Additional
        zdjecia,
        zdjecieGlowne,
        wyrozniowane,
        nowosc,
        flotowy,
        gwarancja
      };

      let result;
      if (editData?.id) {
        result = await busApi.updateListing(editData.id, listingData);
      } else {
        result = await busApi.createListing(listingData);
      }

      if (result.success) {
        toast.success(editData ? 'Ogłoszenie zaktualizowane!' : 'Ogłoszenie dodane!');
        if (onSuccess) onSuccess();
      }
    } catch (error) {
      console.error('Submit error:', error);
      
      // Handle validation errors from backend
      if (error.response?.data?.detail?.errors) {
        setErrors(error.response.data.detail.errors);
        toast.error('Błędy walidacji - sprawdź formularz');
      } else {
        toast.error(error.message || 'Błąd zapisu ogłoszenia');
      }
    } finally {
      setLoading(false);
    }
  };

  // Quill modules for rich text
  const quillModules = useMemo(() => ({
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['link'],
      ['clean']
    ]
  }), []);

  const quillFormats = ['header', 'bold', 'italic', 'underline', 'list', 'bullet', 'link'];

  return (
    <form onSubmit={handleSubmit} className="max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">
        {editData ? 'Edytuj ogłoszenie' : 'Dodaj nowe ogłoszenie'}
      </h2>

      {/* Otomoto Import Section */}
      <div className="mb-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold mb-3 text-blue-900">🚗 Import z Otomoto</h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={otomotoUrl}
            onChange={(e) => setOtomotoUrl(e.target.value)}
            placeholder="https://www.otomoto.pl/..."
            className="flex-1 px-4 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={handleOtomotoImport}
            disabled={importing}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {importing ? 'Importuję...' : 'Importuj dane'}
          </button>
        </div>
        <p className="text-sm text-blue-700 mt-2">
          Wklej URL ogłoszenia z Otomoto, aby automatycznie uzupełnić pola formularza
        </p>
      </div>

      {/* Section Navigation */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {[
          { num: 1, name: 'Informacje podstawowe' },
          { num: 2, name: 'Specyfikacja techniczna' },
          { num: 3, name: 'Stan i historia' },
          { num: 4, name: 'Opis sprzedawcy' }
        ].map(section => (
          <button
            key={section.num}
            type="button"
            onClick={() => setActiveSection(section.num)}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
              activeSection === section.num
                ? 'bg-yellow-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {section.num}. {section.name}
          </button>
        ))}
      </div>

      {/* Section 1: Informacje podstawowe */}
      {activeSection === 1 && (
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">1. Informacje podstawowe</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tytuł ogłoszenia <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="np. Renault Master L3H2 2.3 dCi 163 KM"
              maxLength={120}
              className={`w-full px-4 py-2 border rounded-lg ${errors.title ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
            <p className="text-gray-500 text-sm mt-1">{title.length}/120 znaków</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cena (PLN) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={pricePln}
                onChange={(e) => setPricePln(e.target.value)}
                placeholder="52900"
                min="0"
                max="1000000"
                className={`w-full px-4 py-2 border rounded-lg ${errors.pricePln ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.pricePln && <p className="text-red-500 text-sm mt-1">{errors.pricePln}</p>}
              {pricePln && <p className="text-gray-600 text-sm mt-1">{formatNumber(pricePln)} PLN</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rok produkcji <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={productionYear}
                onChange={(e) => setProductionYear(e.target.value)}
                placeholder="2016"
                min="1950"
                max={new Date().getFullYear()}
                className={`w-full px-4 py-2 border rounded-lg ${errors.productionYear ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.productionYear && <p className="text-red-500 text-sm mt-1">{errors.productionYear}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Marka pojazdu <span className="text-red-500">*</span>
              </label>
              <select
                value={make}
                onChange={(e) => setMake(e.target.value)}
                className={`w-full px-4 py-2 border rounded-lg ${errors.make ? 'border-red-500' : 'border-gray-300'}`}
              >
                <option value="">Wybierz markę</option>
                {marki.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              {errors.make && <p className="text-red-500 text-sm mt-1">{errors.make}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Model pojazdu <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="Master"
                maxLength={60}
                className={`w-full px-4 py-2 border rounded-lg ${errors.model ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.model && <p className="text-red-500 text-sm mt-1">{errors.model}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Kolor</label>
              <select
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Wybierz kolor</option>
                {kolory.map(k => <option key={k} value={k}>{k}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Liczba miejsc</label>
              <input
                type="number"
                value={seats}
                onChange={(e) => setSeats(e.target.value)}
                placeholder="3"
                min="1"
                max="9"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numer VIN (17 znaków)
            </label>
            <input
              type="text"
              value={vin}
              onChange={(e) => setVin(e.target.value.toUpperCase())}
              placeholder="VF1XXX12345678901"
              maxLength={17}
              className={`w-full px-4 py-2 border rounded-lg font-mono ${errors.vin ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.vin && <p className="text-red-500 text-sm mt-1">{errors.vin}</p>}
            {vin && <p className="text-gray-500 text-sm mt-1">{vin.length}/17 znaków</p>}
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="installments"
              checked={installmentsAvailable}
              onChange={(e) => setInstallmentsAvailable(e.target.checked)}
              className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
            />
            <label htmlFor="installments" className="ml-2 text-sm font-medium text-gray-700">
              Możliwość zakupu na raty
            </label>
          </div>
        </div>
      )}

      {/* Section 2: Specyfikacja techniczna */}
      {activeSection === 2 && (
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">2. Specyfikacja techniczna</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rodzaj paliwa <span className="text-red-500">*</span>
              </label>
              <select
                value={fuelType}
                onChange={(e) => setFuelType(e.target.value)}
                className={`w-full px-4 py-2 border rounded-lg ${errors.fuelType ? 'border-red-500' : 'border-gray-300'}`}
              >
                {['Diesel', 'Benzyna', 'LPG', 'CNG', 'Hybryda', 'Elektryczny', 'Inne'].map(f => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
              {errors.fuelType && <p className="text-red-500 text-sm mt-1">{errors.fuelType}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Skrzynia biegów <span className="text-red-500">*</span>
              </label>
              <select
                value={gearbox}
                onChange={(e) => setGearbox(e.target.value)}
                className={`w-full px-4 py-2 border rounded-lg ${errors.gearbox ? 'border-red-500' : 'border-gray-300'}`}
              >
                <option value="Manualna">Manualna</option>
                <option value="Automatyczna">Automatyczna</option>
              </select>
              {errors.gearbox && <p className="text-red-500 text-sm mt-1">{errors.gearbox}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Pojemność skokowa (cm³)
              </label>
              <input
                type="number"
                value={engineDisplacementCc}
                onChange={(e) => setEngineDisplacementCc(e.target.value)}
                placeholder="2300"
                min="100"
                max="10000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Moc (KM)
              </label>
              <input
                type="number"
                value={powerHp}
                onChange={(e) => setPowerHp(e.target.value)}
                placeholder="163"
                min="20"
                max="2000"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                DMC (kg)
              </label>
              <input
                type="number"
                value={gvwKg}
                onChange={(e) => setGvwKg(e.target.value)}
                placeholder="3500"
                min="1000"
                max="7500"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Typ nadwozia <span className="text-red-500">*</span>
            </label>
            <select
              value={bodyType}
              onChange={(e) => setBodyType(e.target.value)}
              className={`w-full px-4 py-2 border rounded-lg ${errors.bodyType ? 'border-red-500' : 'border-gray-300'}`}
            >
              <option value="">Wybierz typ</option>
              {['Furgon (blaszak)', 'Furgon (wysoki)', 'Skrzyniowy', 'Kontener', 'Mixto', 'Inne'].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            {errors.bodyType && <p className="text-red-500 text-sm mt-1">{errors.bodyType}</p>}
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="twinRear"
              checked={twinRearWheels}
              onChange={(e) => setTwinRearWheels(e.target.checked)}
              className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
            />
            <label htmlFor="twinRear" className="ml-2 text-sm font-medium text-gray-700">
              Podwójne tylne koła
            </label>
          </div>
        </div>
      )}

      {/* Section 3: Stan i historia */}
      {activeSection === 3 && (
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">3. Stan i historia pojazdu</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Przebieg (km) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={mileageKm}
                onChange={(e) => setMileageKm(e.target.value)}
                placeholder="222000"
                min="0"
                max="1500000"
                className={`w-full px-4 py-2 border rounded-lg ${errors.mileageKm ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.mileageKm && <p className="text-red-500 text-sm mt-1">{errors.mileageKm}</p>}
              {mileageKm && <p className="text-gray-600 text-sm mt-1">{formatNumber(mileageKm)} km</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stan pojazdu <span className="text-red-500">*</span>
              </label>
              <select
                value={conditionStatus}
                onChange={(e) => setConditionStatus(e.target.value)}
                className={`w-full px-4 py-2 border rounded-lg ${errors.conditionStatus ? 'border-red-500' : 'border-gray-300'}`}
              >
                <option value="Nowy">Nowy</option>
                <option value="Używany">Używany</option>
                <option value="Uszkodzony">Uszkodzony</option>
              </select>
              {errors.conditionStatus && <p className="text-red-500 text-sm mt-1">{errors.conditionStatus}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Kraj pochodzenia
              </label>
              <select
                value={originCountry}
                onChange={(e) => setOriginCountry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Wybierz kraj</option>
                {krajePochodzenia.map(k => <option key={k} value={k}>{k}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data pierwszej rejestracji
              </label>
              <DatePicker
                selected={firstRegistrationDate}
                onChange={(date) => setFirstRegistrationDate(date)}
                dateFormat="dd.MM.yyyy"
                placeholderText="DD.MM.RRRR"
                locale="pl"
                showYearDropdown
                yearDropdownItemNumber={50}
                scrollableYearDropdown
                maxDate={new Date()}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Numer rejestracyjny
            </label>
            <input
              type="text"
              value={registrationNumber}
              onChange={(e) => setRegistrationNumber(e.target.value.toUpperCase())}
              placeholder="VS-071-K"
              maxLength={15}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="accidentFree"
                checked={accidentFree}
                onChange={(e) => setAccidentFree(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="accidentFree" className="ml-2 text-sm font-medium text-gray-700">
                Bezwypadkowy
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="hasReg"
                checked={hasRegistrationNumber}
                onChange={(e) => setHasRegistrationNumber(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="hasReg" className="ml-2 text-sm font-medium text-gray-700">
                Ma numer rejestracyjny
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="servicedAso"
                checked={servicedInAso}
                onChange={(e) => setServicedInAso(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="servicedAso" className="ml-2 text-sm font-medium text-gray-700">
                Serwisowany w ASO
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Section 4: Opis sprzedawcy */}
      {activeSection === 4 && (
        <div className="space-y-4">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">4. Opis sprzedawcy</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Opis ogłoszenia (HTML) <span className="text-red-500">*</span>
            </label>
            <ReactQuill
              value={descriptionHtml}
              onChange={setDescriptionHtml}
              modules={quillModules}
              formats={quillFormats}
              placeholder="Wpisz szczegółowy opis pojazdu..."
              className={`bg-white ${errors.descriptionHtml ? 'border-2 border-red-500 rounded-lg' : ''}`}
            />
            {errors.descriptionHtml && <p className="text-red-500 text-sm mt-1">{errors.descriptionHtml}</p>}
            <p className="text-gray-500 text-sm mt-1">
              {descriptionHtml.replace(/<[^>]*>/g, '').length}/10000 znaków
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stan techniczny i wizualny (krótki opis)
            </label>
            <input
              type="text"
              value={techVisualShort}
              onChange={(e) => setTechVisualShort(e.target.value)}
              placeholder="Bardzo dobry stan, gwarancja przebiegu."
              maxLength={280}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
            <p className="text-gray-500 text-sm mt-1">{techVisualShort.length}/280 znaków</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Link do profilu sprzedawcy (Facebook/strona)
            </label>
            <input
              type="url"
              value={sellerProfileUrl}
              onChange={(e) => setSellerProfileUrl(e.target.value)}
              placeholder="https://www.facebook.com/profile.php?id=..."
              maxLength={200}
              className={`w-full px-4 py-2 border rounded-lg ${errors.sellerProfileUrl ? 'border-red-500' : 'border-gray-300'}`}
            />
            {errors.sellerProfileUrl && <p className="text-red-500 text-sm mt-1">{errors.sellerProfileUrl}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ulica/Adres
            </label>
            <input
              type="text"
              value={locationStreet}
              onChange={(e) => setLocationStreet(e.target.value)}
              placeholder="Smyków 88"
              maxLength={120}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Miejscowość <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={locationCity}
                onChange={(e) => setLocationCity(e.target.value)}
                placeholder="Smyków"
                maxLength={60}
                className={`w-full px-4 py-2 border rounded-lg ${errors.locationCity ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.locationCity && <p className="text-red-500 text-sm mt-1">{errors.locationCity}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Województwo <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={locationRegion}
                onChange={(e) => setLocationRegion(e.target.value)}
                placeholder="Świętokrzyskie"
                maxLength={60}
                className={`w-full px-4 py-2 border rounded-lg ${errors.locationRegion ? 'border-red-500' : 'border-gray-300'}`}
              />
              {errors.locationRegion && <p className="text-red-500 text-sm mt-1">{errors.locationRegion}</p>}
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="homeDelivery"
              checked={homeDelivery}
              onChange={(e) => setHomeDelivery(e.target.checked)}
              className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
            />
            <label htmlFor="homeDelivery" className="ml-2 text-sm font-medium text-gray-700">
              Możliwość dostarczenia pod dom
            </label>
          </div>

          {/* Images */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Zdjęcia</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              disabled={uploadingImage}
              className="mb-2"
            />
            {uploadingImage && <p className="text-blue-600">Przesyłanie...</p>}
            
            <div className="grid grid-cols-3 md:grid-cols-5 gap-2 mt-2">
              {zdjecia.map((img, idx) => (
                <div key={idx} className="relative">
                  <img src={img} alt={`Zdjęcie ${idx + 1}`} className="w-full h-24 object-cover rounded" />
                  <button
                    type="button"
                    onClick={() => removeImage(img)}
                    className="absolute top-0 right-0 bg-red-500 text-white p-1 rounded-bl"
                  >
                    ×
                  </button>
                  {img === zdjecieGlowne && (
                    <span className="absolute bottom-0 left-0 bg-green-500 text-white text-xs px-2 py-1">
                      Główne
                    </span>
                  )}
                  {img !== zdjecieGlowne && (
                    <button
                      type="button"
                      onClick={() => setZdjecieGlowne(img)}
                      className="absolute bottom-0 left-0 bg-gray-700 text-white text-xs px-2 py-1"
                    >
                      Ustaw główne
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Additional flags */}
          <div className="space-y-2 pt-4 border-t">
            <h4 className="font-semibold text-gray-800">Dodatkowe opcje:</h4>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="wyrozniowane"
                checked={wyrozniowane}
                onChange={(e) => setWyrozniowane(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="wyrozniowane" className="ml-2 text-sm font-medium text-gray-700">
                Ogłoszenie wyróżnione
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="nowosc"
                checked={nowosc}
                onChange={(e) => setNowosc(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="nowosc" className="ml-2 text-sm font-medium text-gray-700">
                Nowość
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="flotowy"
                checked={flotowy}
                onChange={(e) => setFlotowy(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="flotowy" className="ml-2 text-sm font-medium text-gray-700">
                Pojazd flotowy
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="gwarancja"
                checked={gwarancja}
                onChange={(e) => setGwarancja(e.target.checked)}
                className="w-4 h-4 text-yellow-600 border-gray-300 rounded"
              />
              <label htmlFor="gwarancja" className="ml-2 text-sm font-medium text-gray-700">
                Gwarancja
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Form actions */}
      <div className="flex justify-between mt-8 pt-6 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
        >
          Anuluj
        </button>

        <div className="flex gap-3">
          {activeSection > 1 && (
            <button
              type="button"
              onClick={() => setActiveSection(activeSection - 1)}
              className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              ← Poprzednia sekcja
            </button>
          )}

          {activeSection < 4 && (
            <button
              type="button"
              onClick={() => setActiveSection(activeSection + 1)}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Następna sekcja →
            </button>
          )}

          {activeSection === 4 && (
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3 bg-yellow-500 text-white font-bold rounded-lg hover:bg-yellow-600 disabled:opacity-50"
            >
              {loading ? 'Zapisuję...' : (editData ? 'Zapisz zmiany' : 'Dodaj ogłoszenie')}
            </button>
          )}
        </div>
      </div>
    </form>
  );
};

export default BusFormNew;
