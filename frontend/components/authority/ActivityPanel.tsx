'use client';

import React from 'react';
import { Ship, Anchor, Shield, Radio } from 'lucide-react';

export const ActivityPanel: React.FC = () => {
  const fleetData = [
    { type: 'Mechanized Trawlers', count: 14, status: 'Active near Zone B Ridge', icon: Ship, color: '#2b59d1' },
    { type: 'Artisanal Boats', count: 6, status: 'Nearshore waters (< 15m depth)', icon: Anchor, color: '#2b59d1' },
    { type: 'Coast Guard Interceptors', count: 2, status: 'Patrolling sector boundaries', icon: Shield, color: '#2b59d1' },
    { type: 'Automated AIS Stations', count: 4, status: 'All sensors operational', icon: Radio, color: '#767371' },
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
          FLEET ACTIVITY & SURVEILLANCE
        </span>
        <span style={{ fontSize: '10px', color: '#242424', fontWeight: 600 }}>22 CRAFT TRACKED</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {fleetData.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              style={{
                padding: '12px 14px',
                borderRadius: '16px',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ color: item.color }}>
                  <Icon size={15} />
                </div>
                <div>
                  <h5 style={{ fontSize: '12px', fontWeight: 600, color: '#242424', margin: 0 }}>
                    {item.type}
                  </h5>
                  <span style={{ fontSize: '10px', color: '#767371' }}>{item.status}</span>
                </div>
              </div>

              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), serif',
                  fontSize: '1.25rem',
                  fontWeight: 400,
                  color: '#242424',
                  letterSpacing: '-0.02em',
                }}
              >
                {item.count}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
