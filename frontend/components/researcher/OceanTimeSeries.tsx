'use client';

import React from 'react';
import { FishingZone } from '@/types/marine';
import { TrendingUp, X } from 'lucide-react';

interface OceanTimeSeriesProps {
  zone: FishingZone;
  onClose?: () => void;
}

export const OceanTimeSeries: React.FC<OceanTimeSeriesProps> = ({ zone, onClose }) => {
  // 7-day historical timeseries data points
  const days = ['05 Sep', '06 Sep', '07 Sep', '08 Sep', '09 Sep', '10 Sep', '11 Sep'];
  const pfzPoints = [65, 68, 74, 88, 92, 90, zone.opportunity_score];

  return (
    <div
      style={{
        padding: '20px',
        backgroundColor: '#ffffff',
        border: '1px solid #cecac8',
        borderRadius: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        boxShadow: '0 4px 20px rgba(36, 36, 36, 0.08)',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={15} color="#2b59d1" />
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
            Oceanographic Time-Series // {zone.name}
          </h4>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: '#f6f3f1',
              border: '1px solid #cecac8',
              color: '#767371',
              cursor: 'pointer',
              padding: '5px',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X size={13} />
          </button>
        )}
      </div>

      {/* Primary Variable Summary Badges */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '6px',
          padding: '10px 12px',
          borderRadius: '16px',
          backgroundColor: '#f6f3f1',
          border: '1px solid #cecac8',
        }}
      >
        <div>
          <span style={{ fontSize: '9px', color: '#767371', display: 'block', textTransform: 'uppercase' }}>SST</span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#242424' }}>29.9°C</span>
        </div>
        <div>
          <span style={{ fontSize: '9px', color: '#767371', display: 'block', textTransform: 'uppercase' }}>CHLORO</span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#242424' }}>2.3 mg/m³</span>
        </div>
        <div>
          <span style={{ fontSize: '9px', color: '#767371', display: 'block', textTransform: 'uppercase' }}>PFZ SCORE</span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#2b59d1' }}>{zone.opportunity_score}/100</span>
        </div>
        <div>
          <span style={{ fontSize: '9px', color: '#767371', display: 'block', textTransform: 'uppercase' }}>DEPTH</span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#242424' }}>{zone.target_depth_m}m</span>
        </div>
      </div>

      {/* Visual Chart Bars (Pure CSS Sparkline) */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '10px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            PFZ CONVERGENCE STRENGTH (7-DAY TREND)
          </span>
          <span style={{ fontSize: '10px', color: '#2b59d1', fontWeight: 500, textTransform: 'uppercase' }}>
            PEAK CONVERGENCE DAY 5
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '80px', paddingTop: '10px' }}>
          {pfzPoints.map((score, idx) => {
            const isToday = idx === pfzPoints.length - 1;
            return (
              <div key={idx} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                <span style={{ fontSize: '10px', color: isToday ? '#242424' : '#767371', fontWeight: isToday ? 600 : 400 }}>
                  {score}
                </span>
                <div
                  style={{
                    width: '100%',
                    height: `${(score / 100) * 60}px`,
                    backgroundColor: isToday ? '#2b59d1' : '#cfdaf5',
                    borderRadius: '4px',
                    border: '1px solid #cecac8',
                  }}
                />
                <span style={{ fontSize: '9px', color: '#767371', whiteSpace: 'nowrap' }}>
                  {days[idx].split(' ')[0]}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
