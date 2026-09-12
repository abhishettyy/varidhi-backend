'use client';

import React from 'react';
import { FishingZone } from '@/types/marine';
import { Badge } from '@/components/common/Badge';
import { MetricCard } from '@/components/common/MetricCard';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  Fish,
  Scale,
  Database,
  CheckCircle2,
  Lock,
} from 'lucide-react';

interface ZoneDetailDrawerProps {
  zone: FishingZone | null;
  onClose: () => void;
}

export const ZoneDetailDrawer: React.FC<ZoneDetailDrawerProps> = ({ zone, onClose }) => {
  if (!zone) return null;

  const isRecommended = zone.status === 'recommended';
  const isHighRisk = zone.status === 'high_risk';
  const isRestricted = zone.status === 'restricted';

  return (
    <aside
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        bottom: 16,
        width: 400,
        zIndex: 20,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f6f3f1',
        border: '1px solid #cecac8',
        borderRadius: '24px',
        boxShadow: '0 10px 30px rgba(36, 36, 36, 0.1)',
        overflow: 'hidden',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Top Header */}
      <div
        style={{
          padding: '18px 22px',
          borderBottom: '1px solid #cecac8',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '12px',
          backgroundColor: '#f6f3f1',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span
              style={{
                fontSize: '10px',
                fontWeight: 600,
                letterSpacing: '0.06em',
                color: '#767371',
                textTransform: 'uppercase',
              }}
            >
              CANDIDATE ZONE INSPECTOR
            </span>
          </div>
          <h2
            style={{
              fontFamily: 'var(--font-untitled-serif), serif',
              fontSize: '1.35rem',
              fontWeight: 400,
              color: '#242424',
              lineHeight: 1.2,
              letterSpacing: '-0.02em',
              margin: 0,
            }}
          >
            {zone.name}
          </h2>
          <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Badge status={zone.status} size="sm" />
            <Badge status={zone.legal_status} size="sm" />
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            background: '#ffffff',
            border: '1px solid #cecac8',
            color: '#767371',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '9999px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
        >
          <X size={15} />
        </button>
      </div>

      {/* Scrollable Content Body */}
      <div style={{ padding: '18px 22px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        {/* Metric Scores Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <MetricCard
            label="Opportunity"
            value={zone.opportunity_score}
            unit="/ 100"
            subtext="Biophysical front match"
          />
          <MetricCard
            label="Marine Safety"
            value={zone.safety_score}
            unit="/ 100"
            subtext={zone.safety_score < 50 ? 'Wave / wind risk' : 'Safe craft envelope'}
          />
          <MetricCard
            label="Port Distance"
            value={zone.distance_km}
            unit="km"
            subtext={`Bearing: ${zone.bearing}`}
          />
          <MetricCard
            label="Seafloor Depth"
            value={zone.target_depth_m}
            unit="m"
            subtext="Bathymetry target"
          />
        </div>

        {/* Legal Status Notice */}
        {isRestricted ? (
          <div
            style={{
              padding: '14px 16px',
              borderRadius: '16px',
              backgroundColor: '#ffffff',
              border: '1px solid #cecac8',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#767371', fontWeight: 600, fontSize: '11px', marginBottom: '4px', textTransform: 'uppercase' }}>
              <Lock size={13} />
              <span>LEGAL RESTRICTION OVERRIDE</span>
            </div>
            <p style={{ fontSize: '12px', color: '#242424', lineHeight: 1.5, margin: 0 }}>
              Commercial and mechanized fishing is prohibited in this zone due to wildlife sanctuary boundaries. Legal compliance strictly overrides biological scores.
            </p>
          </div>
        ) : isHighRisk ? (
          <div
            style={{
              padding: '14px 16px',
              borderRadius: '16px',
              backgroundColor: 'rgba(255, 148, 115, 0.12)',
              border: '1px solid #ff9473',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#242424', fontWeight: 600, fontSize: '11px', marginBottom: '4px', textTransform: 'uppercase' }}>
              <AlertTriangle size={13} color="#ff9473" />
              <span>HYDRODYNAMIC SAFETY WARNING</span>
            </div>
            <p style={{ fontSize: '12px', color: '#242424', lineHeight: 1.5, margin: 0 }}>
              Despite favorable biomass density, this zone is disqualified from primary recommendation due to wave height exceeding safe craft envelopes.
            </p>
          </div>
        ) : (
          <div
            style={{
              padding: '14px 16px',
              borderRadius: '16px',
              backgroundColor: '#cfdaf5',
              border: '1px solid #cecac8',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#2b59d1', fontWeight: 600, fontSize: '11px', marginBottom: '4px', textTransform: 'uppercase' }}>
              <ShieldCheck size={13} />
              <span>PRIMARY RECOMMENDATION</span>
            </div>
            <p style={{ fontSize: '12px', color: '#242424', lineHeight: 1.5, margin: 0 }}>
              Zone B presents the optimal balance of biological productivity and calm hydrodynamic safety within reachable port radius.
            </p>
          </div>
        )}

        {/* Species Target */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>
            <Fish size={13} color="#2b59d1" />
            <span>Target Species</span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {zone.species.map((s, idx) => (
              <span
                key={idx}
                style={{
                  fontSize: '11px',
                  padding: '4px 10px',
                  borderRadius: '9999px',
                  backgroundColor: '#ffffff',
                  border: '1px solid #cecac8',
                  color: '#242424',
                  fontWeight: 500,
                }}
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* Decision Engine Reasons */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>
            <Scale size={13} color="#2b59d1" />
            <span>AI Decision Rationale</span>
          </div>
          <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '8px', margin: 0 }}>
            {zone.reasons.map((r, idx) => (
              <li
                key={idx}
                style={{
                  fontSize: '12px',
                  color: '#242424',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                  lineHeight: 1.45,
                }}
              >
                <CheckCircle2 size={13} color="#2b59d1" style={{ marginTop: '2px', flexShrink: 0 }} />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Scientific Evidence Metadata */}
        {zone.evidence && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', marginBottom: '8px' }}>
              <Database size={13} color="#2b59d1" />
              <span>Scientific Data Provenance</span>
            </div>
            <div
              style={{
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                border: '1px solid #cecac8',
                padding: '12px 14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                fontSize: '11px',
              }}
            >
              <div>
                <span style={{ color: '#767371' }}>PFZ Source: </span>
                <span style={{ color: '#242424', fontWeight: 500 }}>{zone.evidence.pfz_source}</span>
              </div>
              <div>
                <span style={{ color: '#767371' }}>Thermal Gradient: </span>
                <span style={{ color: '#242424', fontWeight: 500 }}>{zone.evidence.sst_front}</span>
              </div>
              <div>
                <span style={{ color: '#767371' }}>Chlorophyll-a: </span>
                <span style={{ color: '#242424', fontWeight: 500 }}>{zone.evidence.chlorophyll}</span>
              </div>
              <div>
                <span style={{ color: '#767371' }}>Weather Check: </span>
                <span style={{ color: '#242424', fontWeight: 500 }}>{zone.evidence.weather_condition}</span>
              </div>
              <div>
                <span style={{ color: '#767371' }}>Sanctuary Exclusion: </span>
                <span style={{ color: '#242424', fontWeight: 500 }}>{zone.evidence.restriction_check}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
