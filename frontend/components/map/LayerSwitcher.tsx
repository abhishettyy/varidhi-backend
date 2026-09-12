'use client';

import React, { useState } from 'react';
import { LayerVisibility } from '@/types/map';
import { Layers, ChevronDown, ChevronUp } from 'lucide-react';

interface LayerSwitcherProps {
  visibility: LayerVisibility;
  onChange: (updated: LayerVisibility) => void;
}

export const LayerSwitcher: React.FC<LayerSwitcherProps> = ({ visibility, onChange }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const toggleLayer = (layerKey: keyof LayerVisibility) => {
    onChange({
      ...visibility,
      [layerKey]: !visibility[layerKey],
    });
  };

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        width: isExpanded ? 250 : 130,
        zIndex: 10,
        padding: '12px 16px',
        backgroundColor: '#f6f3f1',
        borderRadius: '20px',
        border: '1px solid #cecac8',
        boxShadow: '0 4px 16px rgba(36, 36, 36, 0.08)',
        userSelect: 'none',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={15} color="#242424" />
          <span style={{ fontSize: '11px', fontWeight: 600, color: '#242424', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            LAYERS
          </span>
        </div>
        <div
          style={{
            width: 20,
            height: 20,
            borderRadius: '9999px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#767371',
          }}
        >
          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
      </div>

      {isExpanded && (
        <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {/* Active GIS Layers */}
          <div style={{ fontSize: '9px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            CORE GIS LAYERS
          </div>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: '11px',
              color: visibility.zones ? '#242424' : '#767371',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: '#2b59d1' }} />
              Candidate Zones
            </span>
            <input
              type="checkbox"
              checked={visibility.zones}
              onChange={() => toggleLayer('zones')}
              style={{ cursor: 'pointer', accentColor: '#2b59d1' }}
            />
          </label>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: '11px',
              color: visibility.pfz ? '#242424' : '#767371',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: '#2b59d1' }} />
              PFZ Front Forecast
            </span>
            <input
              type="checkbox"
              checked={visibility.pfz}
              onChange={() => toggleLayer('pfz')}
              style={{ cursor: 'pointer', accentColor: '#2b59d1' }}
            />
          </label>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: '11px',
              color: visibility.restrictions ? '#242424' : '#767371',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: 7, height: 7, borderRadius: '2px', backgroundColor: '#767371' }} />
              Protected Sanctuaries
            </span>
            <input
              type="checkbox"
              checked={visibility.restrictions}
              onChange={() => toggleLayer('restrictions')}
              style={{ cursor: 'pointer', accentColor: '#2b59d1' }}
            />
          </label>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: '11px',
              color: visibility.weather ? '#242424' : '#767371',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: '#ff9473' }} />
              Wind / Wave Swell
            </span>
            <input
              type="checkbox"
              checked={visibility.weather}
              onChange={() => toggleLayer('weather')}
              style={{ cursor: 'pointer', accentColor: '#2b59d1' }}
            />
          </label>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: '11px',
              color: visibility.vessels ? '#242424' : '#767371',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: 7, height: 7, borderRadius: '2px', backgroundColor: '#2b59d1' }} />
              AIS Fleet Tracking
            </span>
            <input
              type="checkbox"
              checked={visibility.vessels}
              onChange={() => toggleLayer('vessels')}
              style={{ cursor: 'pointer', accentColor: '#2b59d1' }}
            />
          </label>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              fontSize: '11px',
              color: visibility.cyclone ? '#242424' : '#767371',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', backgroundColor: '#ff9473' }} />
              Depression Rings
            </span>
            <input
              type="checkbox"
              checked={visibility.cyclone}
              onChange={() => toggleLayer('cyclone')}
              style={{ cursor: 'pointer', accentColor: '#2b59d1' }}
            />
          </label>
        </div>
      )}
    </div>
  );
};
