'use client';

import React from 'react';
import { FishingZone } from '@/types/marine';
import { AlertOctagon, Lock, ArrowRight } from 'lucide-react';

interface AlternativeZoneCardProps {
  zone: FishingZone;
  onSelect?: () => void;
}

export const AlternativeZoneCard: React.FC<AlternativeZoneCardProps> = ({ zone, onSelect }) => {
  const isRestricted = zone.legal_status === 'restricted' || zone.status === 'restricted';
  const isHighRisk = zone.status === 'high_risk';

  const markerColor = isRestricted ? '#767371' : isHighRisk ? '#ff9473' : '#2b59d1';
  const washBg = isRestricted ? '#f6f3f1' : isHighRisk ? 'rgba(255, 148, 115, 0.12)' : '#cfdaf5';

  return (
    <div
      style={{
        padding: '16px 18px',
        borderRadius: '20px',
        backgroundColor: '#ffffff',
        border: '1px solid #cecac8',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: '9999px',
              backgroundColor: washBg,
              border: '1px solid #cecac8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: markerColor,
            }}
          >
            {isRestricted ? <Lock size={13} /> : <AlertOctagon size={13} />}
          </div>
          <div>
            <h4
              style={{
                fontFamily: 'var(--font-untitled-serif), serif',
                fontSize: '15px',
                fontWeight: 400,
                color: '#242424',
                margin: 0,
                letterSpacing: '-0.01em',
              }}
            >
              {zone.code}: {zone.name.split('-')[1]?.trim() || zone.name}
            </h4>
            <span style={{ fontSize: '11px', color: '#767371' }}>
              {zone.distance_km} km {zone.bearing} • Opportunity {zone.opportunity_score}/100
            </span>
          </div>
        </div>

        <span
          style={{
            fontSize: '10px',
            padding: '3px 10px',
            borderRadius: '9999px',
            fontWeight: 500,
            backgroundColor: washBg,
            color: markerColor,
            border: '1px solid #cecac8',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
          }}
        >
          {isRestricted ? 'Restricted' : isHighRisk ? 'Caution' : 'Candidate'}
        </span>
      </div>

      <p style={{ margin: 0, fontSize: '12px', color: '#767371', lineHeight: 1.5 }}>
        {zone.reasons?.[0] || (isRestricted ? 'Inside Marine Protected Sanctuary boundary' : 'Elevated hydrodynamic sea state')}
      </p>

      {onSelect && (
        <button
          type="button"
          onClick={onSelect}
          style={{
            alignSelf: 'flex-start',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 12px',
            borderRadius: '100px',
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            color: '#242424',
            fontSize: '11px',
            fontFamily: 'inherit',
            fontWeight: 500,
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#f6f3f1')}
        >
          <span>INSPECT ZONE</span>
          <ArrowRight size={11} />
        </button>
      )}
    </div>
  );
};
