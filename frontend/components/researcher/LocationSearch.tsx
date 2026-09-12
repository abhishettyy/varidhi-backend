'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, Anchor, X } from 'lucide-react';
import { GeocodingResult } from '@/services/geocoding/types';
import { getSuggestedLocations, geocodeLocation } from '@/services/geocoding';

interface LocationSearchProps {
  currentLocationName?: string;
  onSelectLocation: (result: GeocodingResult) => void;
}

export const LocationSearch: React.FC<LocationSearchProps> = ({
  currentLocationName = 'Mangalore',
  onSelectLocation,
}) => {
  const [query, setQuery] = useState(currentLocationName);
  const [suggestions, setSuggestions] = useState<GeocodingResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setQuery(currentLocationName);
  }, [currentLocationName]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    if (val.trim().length > 0) {
      const results = await getSuggestedLocations(val);
      setSuggestions(results);
      setIsOpen(true);
    } else {
      setSuggestions([]);
      setIsOpen(false);
    }
  };

  const handleFocus = async () => {
    setIsFocused(true);
    const results = await getSuggestedLocations(query);
    setSuggestions(results);
    setIsOpen(true);
  };

  const handleSelect = (item: GeocodingResult) => {
    setQuery(item.short_name);
    setIsOpen(false);
    onSelectLocation(item);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    const match = await geocodeLocation(query);
    if (match) {
      handleSelect(match);
    }
  };

  return (
    <div ref={containerRef} style={{ position: 'relative', width: 260, fontFamily: 'var(--font-abc-diatype-mono), monospace' }}>
      <form onSubmit={handleSubmit} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={() => setIsFocused(false)}
          placeholder="Search coastal port..."
          suppressHydrationWarning
          style={{
            width: '100%',
            padding: '7px 28px 7px 32px',
            borderRadius: '100px',
            border: `1px solid ${isFocused ? '#2b59d1' : '#cecac8'}`,
            backgroundColor: '#ffffff',
            color: '#242424',
            fontSize: '12px',
            fontFamily: 'inherit',
            outline: 'none',
            boxShadow: isFocused ? '0 0 0 1px #2b59d1' : 'none',
            transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
          }}
        />
        <Search
          size={13}
          color="#767371"
          style={{ position: 'absolute', left: 12, pointerEvents: 'none' }}
        />
        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery('');
              setSuggestions([]);
            }}
            style={{
              position: 'absolute',
              right: 10,
              background: 'none',
              border: 'none',
              color: '#767371',
              cursor: 'pointer',
              padding: '2px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <X size={12} />
          </button>
        )}
      </form>

      {/* Autocomplete Suggestions Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            right: 0,
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            border: '1px solid #cecac8',
            boxShadow: '0 8px 24px rgba(36, 36, 36, 0.1)',
            maxHeight: '220px',
            overflowY: 'auto',
            zIndex: 50,
            padding: '6px',
          }}
        >
          {suggestions.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleSelect(item)}
              style={{
                padding: '8px 12px',
                borderRadius: '100px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'background-color 0.12s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f6f3f1')}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
            >
              <Anchor size={12} color="#2b59d1" />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '11px', fontWeight: 500, color: '#242424' }}>
                  {item.short_name}
                </div>
                <div style={{ fontSize: '9px', color: '#767371', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {item.state ? `${item.state}, ` : ''}{item.country}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
