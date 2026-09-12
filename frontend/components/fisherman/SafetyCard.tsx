'use client';

import React from 'react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { ShieldCheck, Wind, Waves, Compass, Clock } from 'lucide-react';

export const SafetyCard: React.FC = () => {
  return (
    <div
      style={{
        padding: '22px',
        borderRadius: '24px',
        backgroundColor: '#ffffff',
        border: '1px solid #cecac8',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: '9999px',
              backgroundColor: '#cfdaf5',
              border: '1px solid #cecac8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#2b59d1',
            }}
          >
            <ShieldCheck size={16} />
          </div>
          <div>
            <span
              style={{
                fontSize: '10px',
                color: '#767371',
                textTransform: 'uppercase',
                fontWeight: 600,
                letterSpacing: '0.05em',
                display: 'block',
              }}
            >
              VESSEL SAFETY VERDICT
            </span>
            <h4
              style={{
                fontFamily: 'var(--font-untitled-serif), serif',
                fontSize: '1.15rem',
                fontWeight: 400,
                color: '#242424',
                lineHeight: 1.2,
                margin: 0,
                letterSpacing: '-0.02em',
              }}
            >
              Safe to Venture (Morning Window)
            </h4>
          </div>
        </div>

        <StatusBadge type="safety" value="safe_green" size="sm" />
      </div>

      <p style={{ fontSize: '12px', color: '#767371', lineHeight: 1.6, margin: 0 }}>
        Hydrodynamic models indicate calm coastal waters suitable for motorized artisanal craft during early hours.
        Wave crests projected to increase after 14:00 IST.
      </p>

      {/* Safety Factors Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '10px',
          padding: '12px 14px',
          borderRadius: '16px',
          backgroundColor: '#f6f3f1',
          border: '1px solid #cecac8',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <Waves size={14} color="#2b59d1" />
          <span style={{ color: '#767371' }}>WAVE:</span>
          <span style={{ color: '#242424', fontWeight: 600 }}>1.1 m (Low Swell)</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <Wind size={14} color="#2b59d1" />
          <span style={{ color: '#767371' }}>WIND:</span>
          <span style={{ color: '#242424', fontWeight: 600 }}>11 kts NNW</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <Compass size={14} color="#2b59d1" />
          <span style={{ color: '#767371' }}>CURRENT:</span>
          <span style={{ color: '#242424', fontWeight: 600 }}>0.4 kts South</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
          <Clock size={14} color="#2b59d1" />
          <span style={{ color: '#767371' }}>RETURN:</span>
          <span style={{ color: '#242424', fontWeight: 600 }}>14:30 IST</span>
        </div>
      </div>
    </div>
  );
};
