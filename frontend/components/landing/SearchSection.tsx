'use client';

import React, { useState } from 'react';
import { Search, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';

export const SearchSection: React.FC = () => {
  const router = useRouter();
  const [query, setQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    const lower = query.toLowerCase();
    if (lower.includes('authority') || lower.includes('vessel') || lower.includes('traffic')) {
      router.push('/authority');
    } else if (lower.includes('research') || lower.includes('gis') || lower.includes('sst') || lower.includes('layer')) {
      router.push('/researcher');
    } else {
      router.push('/fisherman');
    }
  };

  return (
    <section
      style={{
        width: '100%',
        backgroundColor: '#ffffff',
        padding: '48px 24px 36px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
      }}
    >
      <h2
        style={{
          fontSize: '1.75rem',
          fontWeight: 700,
          color: '#1e293b',
          marginBottom: '20px',
          letterSpacing: '-0.01em',
        }}
      >
        Search Content
      </h2>

      {/* Search Input Box */}
      <form
        onSubmit={handleSearch}
        style={{
          maxWidth: '680px',
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          backgroundColor: '#ffffff',
          border: '1px solid #94a3b8',
          borderRadius: '2px',
          padding: '10px 16px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        }}
      >
        <Search size={18} color="#64748b" style={{ marginRight: '12px', flexShrink: 0 }} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g., "I am near Mangalore. Where should I fish tomorrow morning?"'
          style={{
            flex: 1,
            border: 'none',
            outline: 'none',
            fontSize: '1rem',
            color: '#1e293b',
            fontFamily: 'inherit',
          }}
        />
        {query.trim() && (
          <button
            type="submit"
            style={{
              background: '#0f766e',
              border: 'none',
              color: '#ffffff',
              padding: '6px 14px',
              borderRadius: '3px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>Search</span>
            <ArrowRight size={14} />
          </button>
        )}
      </form>
    </section>
  );
};
