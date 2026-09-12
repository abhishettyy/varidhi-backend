'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, MapPin, Bell } from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';

interface FishermanHeaderProps {
  locationName?: string;
  onOpenAlerts?: () => void;
}

export const FishermanHeader: React.FC<FishermanHeaderProps> = ({
  locationName = 'Near Mangalore (Old Port)',
  onOpenAlerts,
}) => {
  return (
    <header
      style={{
        height: '60px',
        padding: '0 24px',
        backgroundColor: '#f6f3f1',
        borderBottom: '1px solid #cecac8',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 100,
        position: 'relative',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Brand & Persona */}
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
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#cfdaf5';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#ffffff';
          }}
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
              fontWeight: 500,
              border: '1px solid #cecac8',
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
            }}
          >
            FISHERMAN ADVISORY
          </span>
        </div>
      </div>

      {/* Center: Current Port / Location */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '5px 14px',
          borderRadius: '9999px',
          backgroundColor: '#ffffff',
          border: '1px solid #cecac8',
          fontSize: '12px',
        }}
        className="hidden md:flex"
      >
        <MapPin size={13} color="#2b59d1" />
        <span style={{ color: '#767371', textTransform: 'uppercase', fontSize: '10px' }}>HOME PORT:</span>
        <span style={{ fontWeight: 500, color: '#242424' }}>{locationName}</span>
      </div>

      {/* Right: Quick Status Badges */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <StatusBadge type="recommendation" value="recommended" size="sm" />

        {onOpenAlerts && (
          <button
            type="button"
            onClick={onOpenAlerts}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '100px',
              backgroundColor: '#ffffff',
              border: '1px solid #cecac8',
              color: '#242424',
              fontSize: '11px',
              cursor: 'pointer',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              transition: 'background-color 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#cfdaf5';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#ffffff';
            }}
          >
            <Bell size={13} color="#2b59d1" />
            <span>ADVISORIES</span>
          </button>
        )}
      </div>
    </header>
  );
};
