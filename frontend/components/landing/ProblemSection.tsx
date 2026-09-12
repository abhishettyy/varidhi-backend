'use client';

import React from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

export const ProblemSection: React.FC = () => {
  return (
    <section
      id="problem"
      style={{
        width: '100%',
        backgroundColor: '#f6f3f1',
        padding: '72px 24px 96px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
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
              backgroundColor: '#f37a0a',
            }}
          />
          THE CORE CHALLENGE
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
        The Marine Data Paradox: Rich Data, Fragmented Decisions
      </h2>

      {/* 3. Subtitle in ABC Diatype Mono */}
      <p
        style={{
          fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
          fontSize: 'clamp(14px, 1.2vw, 16px)',
          color: '#4e4d4d',
          lineHeight: 1.4,
          maxWidth: '820px',
          textAlign: 'center',
          margin: '0 auto 56px auto',
          letterSpacing: '-0.02em',
        }}
      >
        Government scientific agencies generate petabytes of high-precision satellite imagery and numerical wave models daily. Yet coastal crafts still navigate blind because telemetry remains locked in isolated scientific repositories.
      </p>

      {/* 4. Comparison Cards Grid (40px padding, 40px radius, 1px Ash border) */}
      <div
        style={{
          width: '100%',
          maxWidth: '1280px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: '24px',
        }}
      >
        {/* Left Card: Before Varidhi — Parchment Card */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              marginBottom: '28px',
              borderBottom: '1px solid #cecac8',
              paddingBottom: '20px',
            }}
          >
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#f37a0a',
              }}
            >
              <AlertTriangle size={18} color="#f37a0a" />
            </div>
            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '24px',
                fontWeight: 400,
                color: '#242424',
                margin: 0,
                letterSpacing: '-0.02em',
              }}
            >
              Fragmented Maritime Silos
            </h3>
          </div>

          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '14px',
              letterSpacing: '-0.02em',
            }}
          >
            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Isolated Data Portals: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                Satellite SST on MOSDAC, Wave forecasts on INCOIS, Cyclone bulletins on IMD, AIS on radar displays.
              </span>
            </div>

            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Cryptic Binary Formats: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                NetCDF rasters, HDF5 bands, and isobar contour maps remain unreadable on artisanal craft bridges.
              </span>
            </div>

            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Manual Spatial Correlation: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                Human operators must mentally correlate whether wave crests intersect with thermal convergence lines.
              </span>
            </div>

            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Critical Warning Latency: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                Vital hours lost aggregating multi-agency advisories during sudden cyclonic depressions.
              </span>
            </div>
          </div>
        </div>

        {/* Right Card: With Varidhi — Elevated Periwinkle Mist Card */}
        <div
          className="monad-card-elevated"
          style={{
            backgroundColor: '#cfdaf5',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              marginBottom: '28px',
              borderBottom: '1px solid #cecac8',
              paddingBottom: '20px',
            }}
          >
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                backgroundColor: '#ffffff',
                border: '1px solid #cecac8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#2b59d1',
              }}
            >
              <CheckCircle2 size={18} color="#2b59d1" />
            </div>
            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '24px',
                fontWeight: 400,
                color: '#242424',
                margin: 0,
                letterSpacing: '-0.02em',
              }}
            >
              Varidhi Autonomous Reasoning
            </h3>
          </div>

          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '14px',
              letterSpacing: '-0.02em',
            }}
          >
            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>One Natural Language Query: </span>
              <span style={{ color: '#2b59d1', fontStyle: 'italic', lineHeight: 1.45 }}>
                &ldquo;Is it safe to fish 25 nautical miles offshore tomorrow at dawn?&rdquo;
              </span>
            </div>

            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Multi-Agent Synthesis: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                Concurrent LangGraph nodes inspect SST thermal fronts, wave swell height, cyclone gale radials, and MPAs.
              </span>
            </div>

            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Deterministic Sensor Proof: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                Every verdict is tied directly to raw satellite overpass timestamps and numerical confidence scores.
              </span>
            </div>

            <div>
              <span style={{ fontWeight: 500, color: '#242424' }}>Instant Spatial Alignment: </span>
              <span style={{ color: '#4e4d4d', lineHeight: 1.45 }}>
                Interactive GIS highlights danger buffers, safe return corridors, and high-probability fishing grounds.
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
