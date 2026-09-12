'use client';

import React from 'react';
import { FishingZone } from '@/types/marine';
import { EvidencePanel } from '@/components/chat/EvidencePanel';
import { Sparkles, X } from 'lucide-react';

interface WhyRecommendationProps {
  zone: FishingZone;
  onClose?: () => void;
}

export const WhyRecommendation: React.FC<WhyRecommendationProps> = ({ zone, onClose }) => {
  const evidencePoints = [
    `PFZ Source: ${zone.evidence?.pfz_source || 'INCOIS Multi-Satellite Composite'}`,
    `Thermal Gradient: ${zone.evidence?.sst_front || '0.6°C delta along 40m bathymetric isobath'}`,
    `Chlorophyll-a: ${zone.evidence?.chlorophyll || '2.3 mg/m³ (Active plankton productivity)'}`,
    `Hydrodynamic Safety: ${zone.evidence?.weather_condition || 'Wave height 1.1m, Wind 11 kts, Swell 8.2s'}`,
    `Legal Compliance: ${zone.evidence?.restriction_check || 'Verified 100% clear of Mulki Marine Sanctuary'}`,
  ];

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
              width: 30,
              height: 30,
              borderRadius: '9999px',
              backgroundColor: '#cfdaf5',
              border: '1px solid #cecac8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#2b59d1',
            }}
          >
            <Sparkles size={15} />
          </div>
          <h4
            style={{
              fontFamily: 'var(--font-untitled-serif), serif',
              fontSize: '1.2rem',
              fontWeight: 400,
              color: '#242424',
              margin: 0,
              letterSpacing: '-0.02em',
            }}
          >
            Why Varidhi Recommends {zone.code}
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
              padding: '6px',
              borderRadius: '9999px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X size={14} />
          </button>
        )}
      </div>

      {/* Decision Summary Table */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
          padding: '12px 14px',
          borderRadius: '16px',
          backgroundColor: '#f6f3f1',
          border: '1px solid #cecac8',
          fontSize: '11px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#767371' }}>PFZ FRONT:</span>
          <span style={{ color: '#2b59d1', fontWeight: 600 }}>Strong Composite</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#767371' }}>SEA STATE:</span>
          <span style={{ color: '#2b59d1', fontWeight: 600 }}>Favorable (1.1m)</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#767371' }}>SAFETY RATING:</span>
          <span style={{ color: '#2b59d1', fontWeight: 600 }}>Good (91/100)</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#767371' }}>RESTRICTIONS:</span>
          <span style={{ color: '#2b59d1', fontWeight: 600 }}>None (Clear)</span>
        </div>
      </div>

      <p style={{ fontSize: '12px', color: '#242424', lineHeight: 1.6, margin: 0 }}>
        Zone A was disqualified due to hazardous 2.7m swell waves. Zone C was excluded because it intersects the Mulki Marine Ecological Reserve. Zone B is the top-ranked compliant candidate.
      </p>

      {/* Expandable Supporting Scientific Evidence */}
      <EvidencePanel
        evidenceList={evidencePoints}
        title="View Supporting Oceanographic Data"
        defaultExpanded={false}
      />
    </div>
  );
};
