'use client';

import React from 'react';
import Link from 'next/link';
import { Fish, ShieldAlert, Microscope, Check } from 'lucide-react';

export const PortalsSection: React.FC = () => {
  return (
    <section
      id="portals"
      style={{
        width: '100%',
        backgroundColor: '#f6f3f1',
        padding: '72px 24px 96px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        position: 'relative',
      }}
    >
      {/* 1. Monad Node Pill Tag */}
      <div style={{ marginBottom: '20px' }}>
        <span
          className="monad-node-tag"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '9999px',
            padding: '10px 20px',
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '12px',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            color: '#242424',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: '#2b59d1',
            }}
          />
          ROLE-SPECIFIC WORKSPACES
        </span>
      </div>

      {/* 2. Section Heading in Untitled Serif at Weight 400 Strictly */}
      <h2
        style={{
          fontFamily: 'var(--font-untitled-serif), Georgia, serif',
          fontSize: 'clamp(2.2rem, 3.8vw, 3.2rem)',
          fontWeight: 400,
          color: '#242424',
          letterSpacing: '-0.02em',
          textAlign: 'center',
          margin: '0 0 16px 0',
          lineHeight: 1.2,
        }}
      >
        Select your operational workspace
      </h2>

      {/* 3. Subtitle in ABC Diatype Mono */}
      <p
        style={{
          fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
          fontSize: 'clamp(14px, 1.2vw, 16px)',
          color: '#4e4d4d',
          lineHeight: 1.4,
          maxWidth: '780px',
          textAlign: 'center',
          margin: '0 auto 56px auto',
          letterSpacing: '-0.02em',
        }}
      >
        Different marine stakeholders require distinct layers of abstraction: binary safety verdicts for craft operators, tactical hazard buffers for coastal command, and multi-sensor NetCDF provenance for ocean researchers.
      </p>

      {/* 4. Three Cards Grid (40px padding, 40px radius, 1px Ash border) */}
      <div
        style={{
          width: '100%',
          maxWidth: '1280px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '24px',
          alignItems: 'stretch',
        }}
      >
        {/* CARD 1: Fishermen Portal (Parchment Card) */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            transition: 'border-color 0.15s ease',
          }}
        >
          <div>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#242424',
                marginBottom: '24px',
              }}
            >
              <Fish size={20} color="#242424" />
            </div>

            <div
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                color: '#797776',
                textTransform: 'uppercase',
                letterSpacing: '-0.02em',
                marginBottom: '8px',
              }}
            >
              COASTAL ARTISANAL & TRAWLERS
            </div>

            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '26px',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
                margin: '0 0 12px 0',
              }}
            >
              Fishermen Portal
            </h3>

            <p
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '14px',
                color: '#4e4d4d',
                lineHeight: 1.45,
                margin: '0 0 28px 0',
                letterSpacing: '-0.02em',
              }}
            >
              High-contrast, actionable fishing ground advisories with binary sea safety verdicts and GPS compass headings back to port.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '36px' }}>
              <MonadFeatureItem label="Sea Venturing Rationale:" desc="Binary Yes/No verdicts with wind and swell analysis" />
              <MonadFeatureItem label="INCOIS PFZ Bearings:" desc="Distance, depth contour & species probability" />
              <MonadFeatureItem label="Swell Warnings:" desc="Simplified wave height alerts in meters" />
              <MonadFeatureItem label="Multilingual Advisory:" desc="Kannada, Tamil, Hindi, and English voice synthesis" />
            </div>
          </div>

          <Link
            href="/fisherman"
            className="btn-monad-black"
            style={{
              backgroundColor: '#242424',
              color: '#ffffff',
              borderRadius: '100px',
              padding: '16px 32px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'opacity 0.15s ease',
            }}
          >
            <span>LAUNCH FISHERMAN WORKSPACE</span>
            <span style={{ fontSize: '11px' }}>▸</span>
          </Link>
        </div>

        {/* CARD 2: Elevated Feature Card (Periwinkle Mist Surface with Gradient Wash) */}
        <div
          className="monad-card-elevated"
          style={{
            backgroundColor: '#cfdaf5',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            position: 'relative',
            overflow: 'hidden',
            transition: 'border-color 0.15s ease',
          }}
        >
          {/* Subtle Decorative Gradient Wash */}
          <div
            style={{
              position: 'absolute',
              top: '-30px',
              right: '-30px',
              width: '260px',
              height: '260px',
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(255, 148, 115, 0.4) 0%, rgba(160, 181, 235, 0.5) 50%, rgba(167, 252, 205, 0.3) 100%)',
              filter: 'blur(45px)',
              pointerEvents: 'none',
            }}
          />

          <div style={{ position: 'relative', zIndex: 1 }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#ffffff',
                border: '1px solid #cecac8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#2b59d1',
                marginBottom: '24px',
              }}
            >
              <Microscope size={20} color="#2b59d1" />
            </div>

            <div
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                color: '#2b59d1',
                textTransform: 'uppercase',
                letterSpacing: '-0.02em',
                marginBottom: '8px',
                fontWeight: 500,
              }}
            >
              MULTI-SENSOR GIS ANALYTICS
            </div>

            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '26px',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
                margin: '0 0 12px 0',
              }}
            >
              Researcher GIS Portal
            </h3>

            <p
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '14px',
                color: '#4e4d4d',
                lineHeight: 1.45,
                margin: '0 0 28px 0',
                letterSpacing: '-0.02em',
              }}
            >
              Multi-sensor satellite correlation workspace with thermal gradient edge detection, academic citations, and raw NetCDF export tools.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '36px' }}>
              <MonadFeatureItem label="OCM-3 Chlorophyll Plumes:" desc="13-band radiometer high-resolution imagery" />
              <MonadFeatureItem label="INSAT-3DR SST Thermal Fronts:" desc="Convergence edge detection and delta gradients" />
              <MonadFeatureItem label="Time-Series Analytical Suite:" desc="Chlorophyll vs SST temporal productivity curves" />
              <MonadFeatureItem label="Academic Citation Dossier:" desc="Peer-reviewed algorithms linked directly to ISRO/INCOIS" />
            </div>
          </div>

          {/* Primary Action Button (Lake Blue Pill) */}
          <Link
            href="/researcher"
            className="btn-monad-blue"
            style={{
              backgroundColor: '#2b59d1',
              color: '#ffffff',
              borderRadius: '100px',
              padding: '16px 32px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              position: 'relative',
              zIndex: 1,
              transition: 'opacity 0.15s ease',
            }}
          >
            <span>LAUNCH RESEARCHER GIS</span>
            <span style={{ fontSize: '11px' }}>▸</span>
          </Link>
        </div>

        {/* CARD 3: Authority Portal (Parchment Card) */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            transition: 'border-color 0.15s ease',
          }}
        >
          <div>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#242424',
                marginBottom: '24px',
              }}
            >
              <ShieldAlert size={20} color="#242424" />
            </div>

            <div
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                color: '#797776',
                textTransform: 'uppercase',
                letterSpacing: '-0.02em',
                marginBottom: '8px',
              }}
            >
              COMMAND & SURVEILLANCE
            </div>

            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '26px',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
                margin: '0 0 12px 0',
              }}
            >
              Marine Authority Portal
            </h3>

            <p
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '14px',
                color: '#4e4d4d',
                lineHeight: 1.45,
                margin: '0 0 28px 0',
                letterSpacing: '-0.02em',
              }}
            >
              Tactical operations center for live AIS vessel surveillance, cyclone warning buffers, and emergency maritime recall broadcasts.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '36px' }}>
              <MonadFeatureItem label="Live AIS Vessel Radar:" desc="Real-time monitoring of 22 coastal crafts and patrols" />
              <MonadFeatureItem label="Cyclone Buffer Projection:" desc="IMD depression cones and 150 km gale radius buffer" />
              <MonadFeatureItem label="Sanctuary Geofencing:" desc="Mulki Marine Ecological Reserve compliance alerts" />
              <MonadFeatureItem label="Emergency Recall System:" desc="Automated broadcast dispatch for vessels at risk" />
            </div>
          </div>

          <Link
            href="/authority"
            className="btn-monad-black"
            style={{
              backgroundColor: '#242424',
              color: '#ffffff',
              borderRadius: '100px',
              padding: '16px 32px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'opacity 0.15s ease',
            }}
          >
            <span>LAUNCH AUTHORITY WORKSPACE</span>
            <span style={{ fontSize: '11px' }}>▸</span>
          </Link>
        </div>
      </div>
    </section>
  );
};

const MonadFeatureItem: React.FC<{ label: string; desc: string }> = ({ label, desc }) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '10px',
      fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
      fontSize: '13px',
      letterSpacing: '-0.02em',
    }}
  >
    <div
      style={{
        marginTop: '2px',
        color: '#242424',
        flexShrink: 0,
      }}
    >
      <Check size={14} strokeWidth={2} />
    </div>
    <div style={{ lineHeight: 1.4 }}>
      <span style={{ fontWeight: 500, color: '#242424' }}>{label}</span>{' '}
      <span style={{ color: '#4e4d4d' }}>{desc}</span>
    </div>
  </div>
);
