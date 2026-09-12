'use client';

import React, { useEffect, useState } from 'react';
import { Wind, Waves, Compass, Activity, Thermometer, Navigation } from 'lucide-react';
import { fetchLiveTelemetry, CoastalTelemetry } from '@/services/api/marineApi';

export const SeaConditions: React.FC = () => {
  const [telemetry, setTelemetry] = useState<CoastalTelemetry | null>(null);

  useEffect(() => {
    let mounted = true;
    fetchLiveTelemetry().then((data) => {
      if (mounted) setTelemetry(data);
    });
    return () => {
      mounted = false;
    };
  }, []);

  const metrics = [
    { label: 'WIND SPEED', value: telemetry?.wind_speed_kmh || '33 km/h', sub: telemetry?.wind_direction || 'WSW 245°', icon: Wind, color: '#2b59d1' },
    { label: 'WAVE HEIGHT', value: telemetry?.wave_height_m || '0.8 m', sub: telemetry?.wave_subtext || 'Hs Significant', icon: Waves, color: '#2b59d1' },
    { label: 'SWELL DIR', value: telemetry?.swell_direction || 'SW 222°', sub: telemetry?.swell_period || 'Period 8.2s', icon: Compass, color: '#2b59d1' },
    { label: 'CURRENT', value: telemetry?.current_mps || '0.41 m/s', sub: telemetry?.current_heading || 'Heading 185°', icon: Navigation, color: '#2b59d1' },
    { label: 'SST FRONT', value: telemetry?.sst_celsius || '29.9°C', sub: 'Thermal Delta', icon: Thermometer, color: '#ff9473' },
    { label: 'SEA STATE', value: telemetry?.sea_state || 'SLIGHT', sub: 'WMO Code 3', icon: Activity, color: '#2b59d1' },
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
        <span
          style={{
            fontSize: '10px',
            fontWeight: 600,
            color: '#767371',
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
          }}
        >
          COASTAL TELEMETRY (MANGALORE)
        </span>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '10px',
            color: '#2b59d1',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
          }}
        >
          <span style={{ width: 5, height: 5, borderRadius: '50%', backgroundColor: '#2b59d1' }} />
          LIVE BUOY
        </span>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '8px',
        }}
      >
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              style={{
                padding: '10px 12px',
                borderRadius: '16px',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: m.color }}>
                <Icon size={13} />
                <span style={{ fontSize: '9px', color: '#767371', fontWeight: 600, textTransform: 'uppercase' }}>
                  {m.label}
                </span>
              </div>
              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), serif',
                  fontSize: '17px',
                  fontWeight: 400,
                  color: '#242424',
                  marginTop: '2px',
                }}
              >
                {m.value}
              </span>
              <span style={{ fontSize: '10px', color: '#767371' }}>
                {m.sub}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
