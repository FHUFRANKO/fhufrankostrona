import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { X, SlidersHorizontal, RotateCcw } from 'lucide-react';
import { marki, typyNadwozi } from '../mock';

export const AdvancedFilters = ({ onFiltersChange, buses = [] }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isOpen, setIsOpen] = useState(false);
  
  // Parse filters from URL
  const getInitialFilters = () => {
    const filters = {};
    
    // Marka - może być wielowartościowa
    const markaParam = searchParams.get('marka');
    if (markaParam) {
      filters.marka = markaParam.split(',');
    }
    
    // Typ - może być wielowartościowy
    const typParam = searchParams.get('typ');
    if (typParam) {
      filters.typ = typParam.split(',');
    }
    
    // Price range
    const priceMin = searchParams.get('price_min');
    const priceMax = searchParams.get('price_max');
    if (priceMin) filters.priceMin = parseInt(priceMin);
    if (priceMax) filters.priceMax = parseInt(priceMax);
    
    // Year range  
    const yearMin = searchParams.get('year_min');
    const yearMax = searchParams.get('year_max');
    if (yearMin) filters.yearMin = parseInt(yearMin);
    if (yearMax) filters.yearMax = parseInt(yearMax);
    
    return filters;
  };
  
  const [filters, setFilters] = useState(getInitialFilters);
  
  // Calculate price and year ranges from data
  const getPriceRange = () => {
    if (!buses.length) return { min: 0, max: 200000 };
    const prices = buses.map(bus => bus.cenaBrutto || 0);
    return {
      min: Math.min(...prices),
      max: Math.max(...prices)
    };
  };
  
  const getYearRange = () => {
    if (!buses.length) return { min: 2000, max: 2025 };
    const years = buses.map(bus => bus.rok || 2020);
    return {
      min: Math.min(...years),
      max: Math.max(...years)
    };
  };
  
  const priceRange = getPriceRange();
  const yearRange = getYearRange();
  
  // Count buses by brand (filtered by other criteria)
  const getBrandCounts = () => {
    const counts = {};
    marki.forEach(marka => {
      const count = buses.filter(bus => {
        // Apply all filters except brand
        const matchesTyp = !filters.typ?.length || filters.typ.includes(bus.typNadwozia);
        const matchesPrice = (!filters.priceMin || bus.cenaBrutto >= filters.priceMin) &&
                            (!filters.priceMax || bus.cenaBrutto <= filters.priceMax);
        const matchesYear = (!filters.yearMin || bus.rok >= filters.yearMin) &&
                           (!filters.yearMax || bus.rok <= filters.yearMax);
        
        return bus.marka === marka && matchesTyp && matchesPrice && matchesYear;
      }).length;
      
      counts[marka] = count;
    });
    return counts;
  };
  
  const brandCounts = getBrandCounts();
  
  // Update URL when filters change
  useEffect(() => {
    const newParams = new URLSearchParams();
    
    if (filters.marka?.length) {
      newParams.set('marka', filters.marka.join(','));
    }
    
    if (filters.typ?.length) {
      newParams.set('typ', filters.typ.join(','));
    }
    
    if (filters.priceMin && filters.priceMin > priceRange.min) {
      newParams.set('price_min', filters.priceMin.toString());
    }
    
    if (filters.priceMax && filters.priceMax < priceRange.max) {
      newParams.set('price_max', filters.priceMax.toString());
    }
    
    if (filters.yearMin && filters.yearMin > yearRange.min) {
      newParams.set('year_min', filters.yearMin.toString());
    }
    
    if (filters.yearMax && filters.yearMax < yearRange.max) {
      newParams.set('year_max', filters.yearMax.toString());
    }
    
    setSearchParams(newParams);
    
    // Notify parent component
    if (onFiltersChange) {
      onFiltersChange(filters);
    }
  }, [filters]);
  
  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const toggleArrayFilter = (key, value) => {
    setFilters(prev => {
      const currentArray = prev[key] || [];
      const newArray = currentArray.includes(value)
        ? currentArray.filter(item => item !== value)
        : [...currentArray, value];
      
      return {
        ...prev,
        [key]: newArray.length ? newArray : undefined
      };
    });
  };
  
  const clearFilters = () => {
    setFilters({});
    setSearchParams(new URLSearchParams());
  };
  
  const hasActiveFilters = () => {
    return Object.keys(filters).some(key => {
      const value = filters[key];
      if (Array.isArray(value)) return value.length > 0;
      return value !== undefined && value !== null;
    });
  };
  
  return (
    <div className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        
        {/* Mobile Filter Toggle */}
        <div className="lg:hidden mb-4">
          <Button
            variant="outline"
            onClick={() => setIsOpen(!isOpen)}
            className="w-full justify-between"
          >
            <span className="flex items-center">
              <SlidersHorizontal className="h-4 w-4 mr-2" />
              Filtry ({Object.keys(filters).filter(k => filters[k]).length})
            </span>
          </Button>
        </div>
        
        {/* Filters Container */}
        <div className={`space-y-4 ${isOpen ? 'block' : 'hidden lg:block'}`}>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
            
            {/* Marka Dropdown */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-[#222122]">Marka</Label>
              <Select
                value={filters.marka?.length === 1 ? filters.marka[0] : ''}
                onValueChange={(value) => {
                  if (value) {
                    toggleArrayFilter('marka', value);
                  }
                }}
              >
                <SelectTrigger className="border-[#F3BC30]/30 focus:border-[#F3BC30]">
                  <SelectValue placeholder="Wybierz markę" />
                </SelectTrigger>
                <SelectContent>
                  {marki
                    .filter(marka => brandCounts[marka] > 0)
                    .sort()
                    .map(marka => (
                      <SelectItem key={marka} value={marka}>
                        {marka} ({brandCounts[marka]})
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              
              {/* Selected brands */}
              {filters.marka?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {filters.marka.map(marka => (
                    <Badge
                      key={marka}
                      variant="secondary"
                      className="text-xs cursor-pointer"
                      onClick={() => toggleArrayFilter('marka', marka)}
                    >
                      {marka} <X className="h-3 w-3 ml-1" />
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            
            {/* Typ nadwozia Dropdown */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-[#222122]">Typ nadwozia</Label>
              <Select
                value={filters.typ?.length === 1 ? filters.typ[0] : ''}
                onValueChange={(value) => {
                  if (value) {
                    toggleArrayFilter('typ', value);
                  }
                }}
              >
                <SelectTrigger className="border-[#F3BC30]/30 focus:border-[#F3BC30]">
                  <SelectValue placeholder="Wybierz typ" />
                </SelectTrigger>
                <SelectContent>
                  {typyNadwozi.map(typ => (
                    <SelectItem key={typ} value={typ}>
                      {typ}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {/* Selected types */}
              {filters.typ?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {filters.typ.map(typ => (
                    <Badge
                      key={typ}
                      variant="secondary" 
                      className="text-xs cursor-pointer"
                      onClick={() => toggleArrayFilter('typ', typ)}
                    >
                      {typ} <X className="h-3 w-3 ml-1" />
                    </Badge>
                  ))}
                </div>
              )}
            </div>
            
            {/* Price Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-[#222122]">Cena</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  placeholder="Od"
                  value={filters.priceMin || ''}
                  onChange={(e) => updateFilter('priceMin', parseInt(e.target.value) || undefined)}
                  className="text-xs border-[#F3BC30]/30 focus:border-[#F3BC30]"
                />
                <Input
                  type="number"
                  placeholder="Do"
                  value={filters.priceMax || ''}
                  onChange={(e) => updateFilter('priceMax', parseInt(e.target.value) || undefined)}
                  className="text-xs border-[#F3BC30]/30 focus:border-[#F3BC30]"
                />
              </div>
            </div>

            {/* Year Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-[#222122]">Rok produkcji</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  placeholder="Od"
                  value={filters.yearMin || ''}
                  onChange={(e) => updateFilter('yearMin', parseInt(e.target.value) || undefined)}
                  className="text-xs border-[#F3BC30]/30 focus:border-[#F3BC30]"
                />
                <Input
                  type="number"
                  placeholder="Do"
                  value={filters.yearMax || ''}
                  onChange={(e) => updateFilter('yearMax', parseInt(e.target.value) || undefined)}
                  className="text-xs border-[#F3BC30]/30 focus:border-[#F3BC30]"
                />
              </div>
            </div>
            
          </div>
          
          {/* Clear Filters Button */}
          {hasActiveFilters() && (
            <div className="flex justify-end">
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="text-[#838282] hover:text-[#222122]"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Wyczyść filtry
              </Button>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
};