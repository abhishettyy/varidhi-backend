'use client';

import React from 'react';
import Link from 'next/link';
import { LocationSearch } from './LocationSearch';
import { GeocodingResult } from '@/services/geocoding/types';
import { Compass, Waves, ArrowLeftRight, ArrowLeft } from 'lucide-react';

interface ResearcherHeaderProps {
  currentLocationName: string;
  onSelectLocation: (res: GeocodingResult) => void;
  zoneCount?: number;
}

export const ResearcherHeader: React.FC<ResearcherHeaderProps> = ({
  currentLocationName,
  onSelectLocation,
  zoneCount = 3,
}) => {
  return (
    <header
      style={{
        height: '60px',
        margin: '12px 20px 0 20px',
        padding: '0 20px',
        backgroundColor: '#f6f3f1',
        border: '1px solid #cecac8',
        borderRadius: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 30,
        position: 'relative',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Brand & Mode Identification */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <Link
          href="/"
          title="Return to Main Portal"
          style={{
            color: '#242424',
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
            padding: '6px 12px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            fontSize: '11px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            gap: '6px',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
        >
          <ArrowLeft size={13} />
          <span>PORTAL</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span
            style={{
              fontFamily: 'var(--font-untitled-serif), serif',
              fontSize: '1.25rem',
              fontWeight: 400,
              color: '#242424',
              letterSpacing: '-0.02em',
            }}
          >
            Varidhi
          </span>
          <span
            style={{
              fontSize: '10px',
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: '#cfdaf5',
              color: '#2b59d1',
              border: '1px solid #cecac8',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
            }}
          >
            RESEARCH WORKBENCH
          </span>
        </div>
      </div>

      {/* Geocoding / Harbour Search & Telemetry */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <LocationSearch
          currentLocationName={currentLocationName}
          onSelectLocation={onSelectLocation}
        />

        {/* Sea Status Telemetry Pill */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '5px 14px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            fontSize: '11px',
          }}
          className="hidden md:flex"
        >
          <Waves size={13} color="#2b59d1" />
          <span style={{ color: '#767371', textTransform: 'uppercase', fontSize: '10px' }}>SEA STATE:</span>
          <span style={{ color: '#242424', fontWeight: 500 }}>Normal ($H_s \approx 1.2m$)</span>
        </div>

        {/* Zones Evaluated Badge */}
        <div
          style={{
            fontSize: '11px',
            color: '#767371',
            padding: '5px 12px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
          }}
          className="hidden lg:block"
        >
          <strong style={{ color: '#242424' }}>{zoneCount}</strong> Candidates Active
        </div>
      </div>

      {/* Mode Switcher / Links */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Link
          href="/fisherman"
          style={{
            textDecoration: 'none',
            fontSize: '11px',
            fontWeight: 500,
            padding: '6px 14px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            color: '#242424',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
        >
          <ArrowLeftRight size={13} color="#2b59d1" />
          <span>Fisherman View</span>
        </Link>
      </div>
    </header>
  );
};
