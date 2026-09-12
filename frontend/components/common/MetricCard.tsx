'use client';

import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  trend?: 'up' | 'down' | 'neutral';
  variant?: 'cyan' | 'emerald' | 'amber' | 'rose';
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subtext,
  variant = 'cyan',
  icon,
}) => {
  const getMarkerColor = () => {
    switch (variant) {
      case 'emerald':
        return '#2b59d1'; // Lake Blue
      case 'amber':
        return '#f37a0a'; // Crimson/Amber
      case 'rose':
        return '#ff9473'; // Coral
      case 'cyan':
      default:
        return '#2b59d1'; // Lake Blue
    }
  };

  const markerColor = getMarkerColor();

  return (
    <div
      className="monad-card"
      style={{
        padding: '20px 24px',
        borderRadius: '24px',
        backgroundColor: '#f6f3f1',
        border: '1px solid #cecac8',
        boxShadow: 'none',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '11px',
            color: '#797776',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
          }}
        >
          {label}
        </span>
        {icon && <span style={{ color: markerColor }}>{icon}</span>}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '2px' }}>
        <span
          style={{
            fontFamily: 'var(--font-untitled-serif), Georgia, serif',
            fontSize: '1.6rem',
            fontWeight: 400,
            color: '#242424',
            letterSpacing: '-0.02em',
          }}
        >
          {value}
        </span>
        {unit && (
          <span
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '12px',
              color: '#4e4d4d',
              letterSpacing: '-0.02em',
            }}
          >
            {unit}
          </span>
        )}
      </div>

      {subtext && (
        <span
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '11px',
            color: '#797776',
            lineHeight: 1.35,
            letterSpacing: '-0.02em',
          }}
        >
          {subtext}
        </span>
      )}
    </div>
  );
};
