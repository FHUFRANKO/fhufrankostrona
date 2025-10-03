import React from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { 
  Star,
  Quote,
  Users,
  TrendingUp,
  Calendar,
  Award
} from 'lucide-react';
import { mockOpinie } from '../mock';

export const OpiniePage = () => {
  const getOcenaStats = () => {
    const totalOpinii = mockOpinie.length;
    const srednia = mockOpinie.reduce((sum, opinia) => sum + opinia.ocena, 0) / totalOpinii;
    const rozkład = {
      5: mockOpinie.filter(o => o.ocena === 5).length,
      4: mockOpinie.filter(o => o.ocena === 4).length,
      3: mockOpinie.filter(o => o.ocena === 3).length,
      2: mockOpinie.filter(o => o.ocena === 2).length,
      1: mockOpinie.filter(o => o.ocena === 1).length,
    };
    return { totalOpinii, srednia, rozkład };
  };

  const stats = getOcenaStats();

  const renderStars = (ocena) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < ocena ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  const formatData = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-gray-900 to-gray-700 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center p-2 bg-[#F3BC30] rounded-full mb-6">
              <Users className="h-6 w-6 text-[#222122]" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Opinie Naszych <span className="text-[#F3BC30]">Klientów</span>
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
              Sprawdź co mówią o nas firmy, które zaufały FHU FRANKO i kupiły u nas swoje busy dostawcze
            </p>
            <div className="flex justify-center">
              <a
                href="/kontakt"
                className="inline-flex items-center px-6 py-3 border border-[#F3BC30] text-base font-medium rounded-md text-[#F3BC30] bg-transparent hover:bg-[#F3BC30] hover:text-[#222122] transition-colors duration-200"
              >
                <Star className="h-5 w-5 mr-2" />
                Dodaj swoją opinię
              </a>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Statystyki */}
        <div className="mb-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {/* Średnia ocen */}
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="inline-flex items-center justify-center p-3 bg-[#F3BC30] rounded-full mb-4">
                  <Award className="h-6 w-6 text-[#222122]" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stats.srednia.toFixed(1)}
                </div>
                <div className="flex justify-center mb-2">
                  {renderStars(Math.round(stats.srednia))}
                </div>
                <p className="text-sm text-gray-600">Średnia ocen</p>
              </CardContent>
            </Card>

            {/* Liczba opinii */}
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="inline-flex items-center justify-center p-3 bg-blue-100 rounded-full mb-4">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stats.totalOpinii}
                </div>
                <p className="text-sm text-gray-600">Zadowolonych klientów</p>
              </CardContent>
            </Card>

            {/* Oceny 5 gwiazdek */}
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="inline-flex items-center justify-center p-3 bg-green-100 rounded-full mb-4">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {Math.round((stats.rozkład[5] / stats.totalOpinii) * 100)}%
                </div>
                <p className="text-sm text-gray-600">Ocen 5 gwiazdek</p>
              </CardContent>
            </Card>

            {/* Od kiedy obsługujemy */}
            <Card className="text-center p-6">
              <CardContent className="p-0">
                <div className="inline-flex items-center justify-center p-3 bg-purple-100 rounded-full mb-4">
                  <Calendar className="h-6 w-6 text-purple-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  15+
                </div>
                <p className="text-sm text-gray-600">Lat doświadczenia</p>
              </CardContent>
            </Card>
          </div>

          {/* Rozkład ocen */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Rozkład ocen</h3>
            <div className="space-y-3">
              {[5, 4, 3, 2, 1].map(rating => (
                <div key={rating} className="flex items-center">
                  <div className="flex items-center w-20">
                    <span className="text-sm font-medium mr-2">{rating}</span>
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                  </div>
                  <div className="flex-1 mx-4">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-[#F3BC30] h-2 rounded-full" 
                        style={{ 
                          width: `${(stats.rozkład[rating] / stats.totalOpinii) * 100}%` 
                        }}
                      />
                    </div>
                  </div>
                  <div className="w-12 text-right">
                    <span className="text-sm text-gray-600">{stats.rozkład[rating]}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Lista opinii */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Co mówią nasi klienci
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockOpinie.map((opinia) => (
              <Card key={opinia.id} className="h-full hover:shadow-lg transition-shadow duration-200">
                <CardContent className="p-6">
                  {/* Header z oceną */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-1">
                      {renderStars(opinia.ocena)}
                    </div>
                    <Quote className="h-5 w-5 text-[#F3BC30]" />
                  </div>

                  {/* Komentarz */}
                  <blockquote className="text-gray-700 mb-4 italic">
                    "{opinia.komentarz}"
                  </blockquote>

                  {/* Autor i branża */}
                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-gray-900">{opinia.autor}</p>
                        <p className="text-sm text-gray-600">{opinia.branza}</p>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {formatData(opinia.data)}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <Card className="bg-gradient-to-r from-[#F3BC30] to-[#E0AA2B] text-[#222122] p-8">
            <CardContent className="p-0">
              <h3 className="text-2xl font-bold mb-4">
                Dołącz do naszych zadowolonych klientów!
              </h3>
              <p className="text-lg mb-6 opacity-90">
                Znajdź idealny bus dostawczy dla swojej firmy w naszej ofercie
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="/ogloszenia"
                  className="inline-flex items-center justify-center px-6 py-3 border border-[#222122] text-base font-medium rounded-md text-[#222122] bg-white hover:bg-gray-50 transition-colors"
                >
                  Zobacz ofertę busów
                </a>
                <a
                  href="/kontakt"
                  className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-[#222122] hover:bg-gray-800 transition-colors"
                >
                  Skontaktuj się z nami
                </a>
                <a
                  href="/kontakt"
                  className="inline-flex items-center justify-center px-6 py-3 border-2 border-[#222122] text-base font-medium rounded-md text-[#222122] bg-white hover:bg-[#222122] hover:text-white transition-colors"
                >
                  <Star className="h-4 w-4 mr-2" />
                  Dodaj opinię
                </a>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};