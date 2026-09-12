'use client';

import React, { useState } from 'react';
import { FishingZone } from '@/types/marine';
import { ShieldCheck, Navigation, CheckCircle2, HelpCircle } from 'lucide-react';

interface RecommendationCardProps {
  zone: FishingZone;
  onWhyThisZone?: () => void;
  onViewOnMap?: () => void;
  onNavigate?: () => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  zone,
  onWhyThisZone,
  onViewOnMap,
  onNavigate,
}) => {
  const [navigating, setNavigating] = useState(false);

  const handleNavigateClick = () => {
    setNavigating(true);
    if (onNavigate) onNavigate();
    setTimeout(() => setNavigating(false), 3000);
  };

  return (
    <div
      style={{
        padding: '24px',
        borderRadius: '24px',
        backgroundColor: '#ffffff',
        border: '1px solid #cecac8',
        display: 'flex',
        flexDirection: 'column',
        gap: '18px',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Top Banner Tag */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: '9999px',
              backgroundColor: '#cfdaf5',
              border: '1px solid #cecac8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#2b59d1',
            }}
          >
            <ShieldCheck size={18} />
          </div>
          <div>
            <span
              style={{
                fontSize: '10px',
                color: '#767371',
                fontWeight: 600,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                display: 'block',
              }}
            >
              RECOMMENDED HARVEST DESTINATION
            </span>
            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), serif',
                fontSize: '1.4rem',
                fontWeight: 400,
                color: '#242424',
                lineHeight: 1.15,
                margin: 0,
                letterSpacing: '-0.02em',
              }}
            >
              {zone.name}
            </h3>
          </div>
        </div>

        <span
          style={{
            fontSize: '11px',
            padding: '4px 12px',
            borderRadius: '100px',
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            color: '#242424',
            fontWeight: 500,
            whiteSpace: 'nowrap',
          }}
        >
          {zone.distance_km} km {zone.bearing}
        </span>
      </div>

      {/* Decision Metric Matrix */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '8px',
          padding: '12px 14px',
          borderRadius: '16px',
          backgroundColor: '#f6f3f1',
          border: '1px solid #cecac8',
        }}
      >
        <div>
          <span style={{ fontSize: '10px', color: '#767371', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>
            OPPORTUNITY
          </span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#2b59d1' }}>
            HIGH ({zone.opportunity_score})
          </span>
        </div>

        <div>
          <span style={{ fontSize: '10px', color: '#767371', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>
            SAFETY
          </span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#242424' }}>
            GOOD ({zone.safety_score})
          </span>
        </div>

        <div>
          <span style={{ fontSize: '10px', color: '#767371', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>
            JURISDICTION
          </span>
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#242424' }}>
            ALLOWED
          </span>
        </div>
      </div>

      {/* Primary Reasons Bullets */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#242424' }}>
          <CheckCircle2 size={14} color="#2b59d1" />
          <span>Strong PFZ thermal front indication (INCOIS match)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#242424' }}>
          <CheckCircle2 size={14} color="#2b59d1" />
          <span>Favorable sea conditions (Wave height 1.1m, wind 11 kts)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#242424' }}>
          <CheckCircle2 size={14} color="#2b59d1" />
          <span>Outside all marine reserves & restricted sanctuaries</span>
        </div>
      </div>

      {/* Target Species Pill Tags */}
      {zone.species && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '10px', color: '#767371', textTransform: 'uppercase' }}>SPECIES:</span>
          {zone.species.map((sp, idx) => (
            <span
              key={idx}
              style={{
                fontSize: '11px',
                padding: '3px 10px',
                borderRadius: '100px',
                backgroundColor: '#f6f3f1',
                color: '#242424',
                border: '1px solid #cecac8',
                fontWeight: 500,
              }}
            >
              {sp}
            </span>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '10px', marginTop: '4px' }}>
        {onWhyThisZone && (
          <button
            type="button"
            onClick={onWhyThisZone}
            style={{
              flex: 1,
              padding: '10px 16px',
              borderRadius: '100px',
              border: '1px solid #cecac8',
              backgroundColor: '#ffffff',
              color: '#242424',
              fontSize: '11px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              transition: 'background-color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#f6f3f1')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
          >
            <HelpCircle size={13} color="#767371" />
            <span>RATIONALE</span>
          </button>
        )}

        <button
          type="button"
          onClick={handleNavigateClick}
          style={{
            flex: 1.3,
            padding: '10px 18px',
            borderRadius: '100px',
            border: 'none',
            backgroundColor: navigating ? '#242424' : '#2b59d1',
            color: '#f6f3f1',
            fontSize: '11px',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            transition: 'opacity 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.9')}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
        >
          <Navigation size={13} />
          <span>{navigating ? 'ROUTE ACTIVE' : 'COMMENCE VOYAGE ▸'}</span>
        </button>
      </div>
    </div>
  );
};
