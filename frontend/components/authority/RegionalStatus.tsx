'use client';

import React from 'react';
import { Shield, AlertTriangle, Lock, Waves, Eye, Radio } from 'lucide-react';

export const RegionalStatus: React.FC = () => {
  const kpis = [
    { label: 'Active Alerts', value: '3', sub: '1 Warning, 2 Caution', icon: AlertTriangle, color: '#ff9473' },
    { label: 'High Risk Areas', value: '2', sub: 'Zone A & Offshore Buffer', icon: Shield, color: '#ff9473' },
    { label: 'Restricted Areas', value: '4', sub: 'Mulki Sanctuary + 3 MPAs', icon: Lock, color: '#767371' },
    { label: 'Fishing Activity', value: 'Moderate', sub: '14 Trawlers in Zone B', icon: Waves, color: '#2b59d1' },
    { label: 'Weather Status', value: 'Stable', sub: 'Depression 72 NM WSW', icon: Eye, color: '#2b59d1' },
    { label: 'Patrol Interceptors', value: '2 Active', sub: 'ICG C-421 & CSP KP-08', icon: Radio, color: '#2b59d1' },
  ];

  return (
    <div
      style={{
        padding: '22px',
        borderRadius: '24px',
        backgroundColor: '#ffffff',
        border: '1px solid #cecac8',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <span style={{ fontSize: '10px', fontWeight: 600, color: '#767371', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          REGIONAL OPERATIONAL TELEMETRY
        </span>
        <span style={{ fontSize: '10px', color: '#2b59d1', textTransform: 'uppercase' }}>LIVE AIS SYNC</span>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
        }}
      >
        {kpis.map((k, idx) => {
          const Icon = k.icon;
          return (
            <div
              key={idx}
              style={{
                padding: '12px 14px',
                borderRadius: '16px',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: k.color }}>
                <Icon size={13} />
                <span style={{ fontSize: '9px', color: '#767371', fontWeight: 600, textTransform: 'uppercase' }}>
                  {k.label}
                </span>
              </div>
              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), serif',
                  fontSize: '1.25rem',
                  fontWeight: 400,
                  color: '#242424',
                  marginTop: '2px',
                  letterSpacing: '-0.02em',
                }}
              >
                {k.value}
              </span>
              <span style={{ fontSize: '10px', color: '#767371' }}>{k.sub}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
