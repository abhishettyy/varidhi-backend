'use client';

import React, { useState } from 'react';
import { Info, ChevronDown, ChevronUp } from 'lucide-react';

export const MapLegend: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 24,
        left: 20,
        zIndex: 10,
        padding: '12px 16px',
        width: isExpanded ? 270 : 130,
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
          <Info size={14} color="#242424" />
          <span style={{ fontSize: '11px', fontWeight: 600, color: '#242424', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            MAP LEGEND
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
          <div style={{ fontSize: '9px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            DECISION ENGINE ZONES
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#2b59d1' }} />
            <div>
              <strong style={{ color: '#242424' }}>Zone B</strong>
              <span style={{ color: '#767371' }}>: Recommended</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#ff9473' }} />
            <div>
              <strong style={{ color: '#242424' }}>Zone A</strong>
              <span style={{ color: '#767371' }}>: High Swell Risk</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#767371' }} />
            <div>
              <strong style={{ color: '#242424' }}>Zone C</strong>
              <span style={{ color: '#767371' }}>: Restricted Sanctuary</span>
            </div>
          </div>

          <div style={{ height: 1, backgroundColor: '#cecac8', margin: '2px 0' }} />

          <div style={{ fontSize: '9px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            SPATIAL LAYERS
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: '#767371' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#2b59d1', opacity: 0.85 }} />
            <span>Potential Fishing Zone (PFZ)</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: '#767371' }}>
            <span style={{ width: 12, height: 2, backgroundColor: '#2b59d1', borderRadius: 2 }} />
            <span>Thermal Front Gradient</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: '#767371' }}>
            <span style={{ width: 10, height: 8, backgroundColor: 'rgba(255, 148, 115, 0.15)', border: '1px dashed #ff9473', borderRadius: '2px' }} />
            <span>Marine Protected Area (MPA)</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: '#767371' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#242424' }} />
            <span>Landing Center / Home Port</span>
          </div>
        </div>
      )}
    </div>
  );
};
