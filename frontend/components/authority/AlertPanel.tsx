'use client';

import React from 'react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { ArrowRight } from 'lucide-react';

interface AlertPanelProps {
  onFocusArea?: (areaKey: string) => void;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ onFocusArea }) => {
  const alerts = [
    {
      id: 'alt_1',
      title: 'High Wind Velocity Alert',
      region: 'Coastal Karnataka (Mangalore to Malpe)',
      desc: 'Wind gusts exceeding 24 knots expected post 14:00 UTC. Small craft cautionary advisory active.',
      severity: 'warning_orange',
      key: 'ZONE_A',
      actionText: 'View Hazard Zone',
    },
    {
      id: 'alt_2',
      title: 'Sanctuary Geofence Proximity',
      region: 'Mulki Marine Ecological Reserve',
      desc: '4 fishing craft active within 2.5 NM of northern sanctuary boundary. AIS tracking engaged.',
      severity: 'caution_yellow',
      key: 'ZONE_C',
      actionText: 'Inspect Sanctuary',
    },
    {
      id: 'alt_3',
      title: 'Cyclonic Swell Progression',
      region: 'Arabian Sea (72 NM WSW)',
      desc: 'Deep depression generating 3.4m peripheral swells. Hazard buffer ring projected toward north-northwest.',
      severity: 'danger_red',
      key: 'cyclone',
      actionText: 'Track Depression',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontFamily: 'var(--font-abc-diatype-mono), monospace' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '10px', fontWeight: 600, color: '#767371', letterSpacing: '0.06em', textTransform: 'uppercase' }}>
          ACTIVE MARITIME ALERTS ({alerts.length})
        </span>
        <span style={{ fontSize: '10px', color: '#767371' }}>UPDATED 8M AGO</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {alerts.map((a) => (
          <div
            key={a.id}
            style={{
              padding: '16px 18px',
              borderRadius: '20px',
              backgroundColor: '#ffffff',
              border: '1px solid #cecac8',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
                {a.title}
              </h4>
              <StatusBadge type="safety" value={a.severity} size="sm" />
            </div>

            <span style={{ fontSize: '11px', color: '#2b59d1', fontWeight: 500 }}>
              {a.region}
            </span>

            <p style={{ fontSize: '12px', color: '#767371', lineHeight: 1.5, margin: 0 }}>
              {a.desc}
            </p>

            {onFocusArea && (
              <button
                type="button"
                onClick={() => onFocusArea(a.key)}
                style={{
                  background: '#f6f3f1',
                  border: '1px solid #cecac8',
                  borderRadius: '100px',
                  color: '#242424',
                  fontSize: '11px',
                  fontFamily: 'inherit',
                  fontWeight: 500,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  alignSelf: 'flex-start',
                  padding: '4px 12px',
                  marginTop: '4px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  transition: 'background-color 0.15s ease',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#f6f3f1')}
              >
                <span>{a.actionText}</span>
                <ArrowRight size={11} />
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
