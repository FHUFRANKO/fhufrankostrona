import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  Plus, 
  Edit, 
  Trash2,
  ArrowLeft,
  Truck,
  Star,
  Eye,
  BarChart3,
  MessageSquare,
  LogOut,
  Settings
} from 'lucide-react';
import { busApi } from '../api/busApi';
import BusFormNew from '../components/BusFormNew';
import { OpinionForm } from '../components/OpinionForm';
import { toast } from 'sonner';

export const AdminPanel = () => {
  const navigate = useNavigate();
  const [buses, setBuses] = useState([]);
  const [opinions, setOpinions] = useState([]);
  const [stats, setStats] = useState({ total: 0, wyrozniowane: 0, nowe: 0, flotowe: 0 });
  const [showForm, setShowForm] = useState(false);
  const [showOpinionForm, setShowOpinionForm] = useState(false);
  const [editingBus, setEditingBus] = useState(null);
  const [editingOpinion, setEditingOpinion] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBuses();
    fetchOpinions();
    fetchStats();
  }, []);

  const fetchBuses = async () => {
    try {
      const data = await busApi.getAllBuses();
      setBuses(data);
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Error fetching buses:', error);
        toast.error('Błąd podczas pobierania ogłoszeń');
      }
    }
  };

  const fetchOpinions = async () => {
    try {
      const data = await busApi.getAllOpinions();
      setOpinions(data);
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Error fetching opinions:', error);
        toast.error('Błąd podczas pobierania opinii');
      }
    }
  };

  const fetchStats = async () => {
    try {
      const data = await busApi.getStats();
      setStats(data);
    } catch (error) {
      if (error.response?.status !== 401) {
        console.error('Error fetching stats:', error);
      }
    }
  };

  const handleLogout = async () => {
    try {
      await busApi.logout();
      toast.success('Wylogowano pomyślnie');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Błąd wylogowywania');
    }
  };

  const handleAddBus = () => {
    setEditingBus(null);
    setShowForm(true);
  };

  const handleEditBus = (bus) => {
    setEditingBus(bus);
    setShowForm(true);
  };

  const handleDeleteBus = async (busId) => {
    if (!window.confirm('Czy na pewno chcesz usunąć to ogłoszenie?')) {
      return;
    }

    try {
      await busApi.deleteBus(busId);
      toast.success('Ogłoszenie zostało usunięte');
      fetchBuses();
      fetchStats();
    } catch (error) {
      console.error('Error deleting bus:', error);
      toast.error('Błąd podczas usuwania ogłoszenia');
    }
  };

  const handleToggleSold = async (bus) => {
    try {
      const newSoldStatus = !bus.sold;
      const updateData = { gwarancja: newSoldStatus };
      if (newSoldStatus) {
        updateData.hak = false; // Disable reserved if sold
      }
      await busApi.updateBus(bus.id, updateData); // This endpoint handles toggle properly in backend too if using simplified update, 
      // actually backend expects specific structure but simpler is usually better.
      // Wait, updateBus takes BusUpdate model.
      // BusUpdate has gwarancja/sold mapped.
      
      // Let's use the toggle endpoint for better safety if available, 
      // or map correctly.
      // busApi.toggleSoldStatus(bus.id) exists!
      await busApi.toggleSoldStatus(bus.id);
      
      toast.success(newSoldStatus ? 'Oznaczono jako SPRZEDANE' : 'Odznaczono SPRZEDANE');
      fetchBuses();
    } catch (error) {
      console.error('Error toggling sold status:', error);
      toast.error('Błąd podczas zmiany statusu');
    }
  };

  const handleToggleReserved = async (bus) => {
    try {
      await busApi.toggleReservedStatus(bus.id);
      // Wait, toggleReservedStatus returns new status
      toast.success('Zmieniono status rezerwacji');
      fetchBuses();
    } catch (error) {
      console.error('Error toggling reserved status:', error);
      toast.error('Błąd podczas zmiany statusu');
    }
  };

  const handleSubmitBus = async (busData) => {
    setLoading(true);
    try {
      // busData is from BusFormNew which returns mapped structure ready for API
      if (editingBus) {
        // Use new listing API for updates too?
        // BusFormNew uses busApi.updateListing or createListing internally if passed correct props?
        // Wait, BusFormNew handles submission itself!
        // So I don't need this function?
        // Ah, BusFormNew props: onSuccess, onCancel.
        // It calls API internally.
      }
      // Actually BusFormNew calls API itself.
      // So this function is unused here.
    } catch (error) {
      console.error('Error saving bus:', error);
    } finally {
      setLoading(false);
    }
  };

  // Opinion handlers
  const handleAddOpinion = () => {
    setEditingOpinion(null);
    setShowOpinionForm(true);
  };

  const handleEditOpinion = (opinion) => {
    setEditingOpinion(opinion);
    setShowOpinionForm(true);
  };

  const handleDeleteOpinion = async (opinionId) => {
    if (!window.confirm('Czy na pewno chcesz usunąć tę opinię?')) {
      return;
    }

    try {
      await busApi.deleteOpinion(opinionId);
      toast.success('Opinia została usunięta');
      fetchOpinions();
    } catch (error) {
      console.error('Error deleting opinion:', error);
      toast.error('Błąd podczas usuwania opinii');
    }
  };

  const handleSubmitOpinion = async (opinionData) => {
    setLoading(true);
    try {
      if (editingOpinion) {
        await busApi.updateOpinion(editingOpinion.id, opinionData);
        toast.success('Opinia została zaktualizowana');
      } else {
        await busApi.createOpinion(opinionData);
        toast.success('Opinia została dodana');
      }
      setShowOpinionForm(false);
      setEditingOpinion(null);
      fetchOpinions();
    } catch (error) {
      console.error('Error saving opinion:', error);
      toast.error('Błąd podczas zapisywania opinii');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOpinionForm = () => {
    setShowOpinionForm(false);
    setEditingOpinion(null);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingBus(null);
  };

  if (showOpinionForm) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <Button
            variant="ghost"
            onClick={handleCancelOpinionForm}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Powrót do listy
          </Button>
          <OpinionForm
            initialData={editingOpinion}
            onSubmit={handleSubmitOpinion}
            onCancel={handleCancelOpinionForm}
            loading={loading}
          />
        </div>
      </div>
    );
  }

  if (showForm) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <Button
            variant="ghost"
            onClick={handleCancelForm}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Powrót do listy
          </Button>
          <BusFormNew
            editData={editingBus}
            onSuccess={() => {
              setShowForm(false);
              fetchBuses();
              fetchStats();
            }}
            onCancel={handleCancelForm}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <Settings className="h-6 w-6 text-yellow-500" />
              Panel Admina
            </h1>
            <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">
              Administrator
            </span>
          </div>
          
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => navigate('/')}
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Strona główna
            </Button>
            <Button
              variant="ghost"
              onClick={handleLogout}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Wyloguj
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="bg-white p-1 border rounded-lg shadow-sm">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-white">
              <BarChart3 className="h-4 w-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="ogloszenia" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-white">
              <Truck className="h-4 w-4 mr-2" />
              Ogłoszenia ({stats.total})
            </TabsTrigger>
            <TabsTrigger value="opinie" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-white">
              <MessageSquare className="h-4 w-4 mr-2" />
              Opinie
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6 animate-in fade-in-50 duration-500">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard 
                title="Wszystkie busy" 
                value={stats.total} 
                icon={Truck} 
                color="blue" 
              />
              <StatsCard 
                title="Wyróżnione" 
                value={stats.wyrozniowane} 
                icon={Star} 
                color="yellow" 
              />
              <StatsCard 
                title="Nowe" 
                value={stats.nowe} 
                icon={Plus} 
                color="green" 
              />
              <StatsCard 
                title="Flotowe" 
                value={stats.flotowe} 
                icon={Eye} 
                color="purple" 
              />
            </div>

            <div className="bg-white p-6 rounded-xl border shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Szybkie akcje</h3>
              <div className="flex gap-4">
                <Button onClick={handleAddBus} className="bg-yellow-500 hover:bg-yellow-600 text-white">
                  <Plus className="mr-2 h-4 w-4" />
                  Dodaj nowe ogłoszenie
                </Button>
                <Button onClick={handleAddOpinion} variant="outline">
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Dodaj opinię
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* Ogłoszenia Tab */}
          <TabsContent value="ogloszenia" className="space-y-6 animate-in fade-in-50 duration-500">
            <div className="flex justify-between items-center bg-white p-4 rounded-lg border shadow-sm">
              <h2 className="text-xl font-bold text-gray-800">Zarządzanie flotą</h2>
              <Button
                onClick={handleAddBus}
                className="bg-yellow-500 hover:bg-yellow-600 text-white shadow-md hover:shadow-lg transition-all"
              >
                <Plus className="mr-2 h-4 w-4" />
                Dodaj Bus
              </Button>
            </div>

            {buses.length === 0 ? (
              <EmptyState 
                icon={Truck} 
                title="Brak ogłoszeń" 
                description="Dodaj pierwsze ogłoszenie busa do systemu." 
                action={handleAddBus} 
                actionLabel="Dodaj Bus" 
              />
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {buses.map((bus) => (
                  <BusCardAdmin 
                    key={bus.id} 
                    bus={bus} 
                    onEdit={handleEditBus} 
                    onDelete={handleDeleteBus} 
                    onToggleSold={handleToggleSold} 
                    onToggleReserved={handleToggleReserved} 
                  />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Opinie Tab */}
          <TabsContent value="opinie" className="space-y-6 animate-in fade-in-50 duration-500">
            <div className="flex justify-between items-center bg-white p-4 rounded-lg border shadow-sm">
              <h2 className="text-xl font-bold text-gray-800">Zarządzanie opiniami</h2>
              <Button
                onClick={handleAddOpinion}
                className="bg-yellow-500 hover:bg-yellow-600 text-white shadow-md hover:shadow-lg transition-all"
              >
                <Plus className="mr-2 h-4 w-4" />
                Dodaj Opinię
              </Button>
            </div>

            {opinions.length === 0 ? (
              <EmptyState 
                icon={MessageSquare} 
                title="Brak opinii" 
                description="Dodaj pierwszą opinię klienta." 
                action={handleAddOpinion} 
                actionLabel="Dodaj Opinię" 
              />
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {opinions.map((opinion) => (
                  <OpinionCardAdmin 
                    key={opinion.id} 
                    opinion={opinion} 
                    onEdit={handleEditOpinion} 
                    onDelete={handleDeleteOpinion} 
                  />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

// Sub-components for cleaner code
const StatsCard = ({ title, value, icon: Icon, color }) => {
  const colors = {
    blue: "bg-blue-100 text-blue-600",
    yellow: "bg-yellow-100 text-yellow-600",
    green: "bg-green-100 text-green-600",
    purple: "bg-purple-100 text-purple-600"
  };

  return (
    <Card className="hover:shadow-md transition-shadow border-t-4 border-t-yellow-400">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">{title}</p>
            <h3 className="text-3xl font-bold text-gray-800 mt-2">{value}</h3>
          </div>
          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${colors[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const EmptyState = ({ icon: Icon, title, description, action, actionLabel }) => (
  <Card className="border-dashed">
    <CardContent className="p-12 text-center flex flex-col items-center">
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        <Icon className="h-8 w-8 text-gray-400" />
      </div>
      <h3 className="text-xl font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-sm">{description}</p>
      <Button onClick={action} className="bg-yellow-500 hover:bg-yellow-600 text-white">
        <Plus className="mr-2 h-4 w-4" />
        {actionLabel}
      </Button>
    </CardContent>
  </Card>
);

const BusCardAdmin = ({ bus, onEdit, onDelete, onToggleSold, onToggleReserved }) => (
  <Card className="hover:shadow-md transition-shadow group">
    <CardContent className="p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start sm:items-center space-x-4">
          <div className="relative w-24 h-24 flex-shrink-0">
            {bus.zdjecia && bus.zdjecia.length > 0 ? (
              <img
                src={bus.zdjecia[0]}
                alt={`${bus.marka} ${bus.model}`}
                className="w-full h-full object-cover rounded-lg shadow-sm"
              />
            ) : (
              <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
                <Truck className="h-8 w-8 text-gray-300" />
              </div>
            )}
            {bus.sold && (
              <div className="absolute inset-0 bg-red-500/80 flex items-center justify-center rounded-lg">
                <span className="text-white font-bold text-xs uppercase">Sprzedane</span>
              </div>
            )}
          </div>
          
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h3 className="font-bold text-lg text-gray-800">
                {bus.marka} {bus.model}
              </h3>
              {bus.wyrozniowane && (
                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded border border-yellow-200">
                  Wyróżnione
                </span>
              )}
              {bus.nowosc && (
                <span className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded border border-green-200">
                  Nowość
                </span>
              )}
            </div>
            
            <p className="text-sm text-gray-500 mb-2 flex items-center gap-2">
              <span>{bus.rok} r.</span>
              <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
              <span>{bus.typNadwozia}</span>
              <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
              <span>{bus.przebieg?.toLocaleString()} km</span>
            </p>
            
            <p className="text-lg font-bold text-yellow-600">
              {bus.cenaBrutto?.toLocaleString()} zł
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 w-full sm:w-auto mt-2 sm:mt-0">
          <Button
            variant={bus.sold ? "destructive" : "outline"}
            size="sm"
            onClick={() => onToggleSold(bus)}
            className={`flex-1 sm:flex-none ${!bus.sold && "border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"}`}
          >
            {bus.sold ? 'Odznacz sprzedane' : 'Oznacz jako sprzedane'}
          </Button>
          
          <Button
            variant={bus.reserved ? "secondary" : "outline"}
            size="sm"
            onClick={() => onToggleReserved(bus)}
            disabled={bus.sold}
            className="flex-1 sm:flex-none"
          >
            {bus.reserved ? 'Rezerwacja (Tak)' : 'Rezerwacja (Nie)'}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => onEdit(bus)}
            className="flex-1 sm:flex-none"
          >
            <Edit className="h-4 w-4 mr-2" />
            Edytuj
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(bus.id)}
            className="text-gray-400 hover:text-red-600 hover:bg-red-50 flex-1 sm:flex-none"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
);

const OpinionCardAdmin = ({ opinion, onEdit, onDelete }) => (
  <Card className="hover:shadow-md transition-shadow">
    <CardContent className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-bold text-gray-800">
              {opinion.imie} {opinion.nazwisko}
            </h3>
            <div className="flex text-yellow-400">
              {[...Array(opinion.ocena || 5)].map((_, i) => (
                <Star key={i} className="h-4 w-4 fill-current" />
              ))}
            </div>
            {!opinion.wyswietlaj && (
              <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">
                Ukryta
              </span>
            )}
          </div>
          
          <p className="text-sm text-gray-500 mb-3">
            {opinion.rodzajFirmy || 'Firma'} 
            {opinion.zakupionyPojazd && ` • Pojazd: ${opinion.zakupionyPojazd}`}
          </p>
          
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <p className="text-gray-700 italic text-sm">
              "{opinion.komentarz}"
            </p>
          </div>
        </div>
        
        <div className="flex flex-col gap-2 ml-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onEdit(opinion)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(opinion.id)}
            className="text-gray-400 hover:text-red-600 hover:bg-red-50"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
);
