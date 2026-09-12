'use client';

import React from 'react';
import Link from 'next/link';
import { Activity, ShieldAlert, Satellite } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <section
      style={{
        width: '100%',
        backgroundColor: '#f6f3f1',
        padding: '80px 24px 96px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Monad Gradient Atmospheric Wash (Coral -> Sky Blue softly diffused) */}
      <div
        className="monad-gradient-wash"
        style={{
          width: '640px',
          height: '380px',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'radial-gradient(ellipse at center, rgba(255, 148, 115, 0.45) 0%, rgba(160, 181, 235, 0.35) 50%, rgba(167, 252, 205, 0.15) 80%, transparent 100%)',
          filter: 'blur(75px)',
        }}
      />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '1100px', width: '100%' }}>
        {/* 1. Monad Pipeline Node Tag (Parchment fill, 1px Ash border, 9999px radius) */}
        <div style={{ marginBottom: '28px' }}>
          <div
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
            <span>ISRO SIH 26176</span>
            <span style={{ color: '#cecac8' }}>|</span>
            <span style={{ color: '#4e4d4d' }}>AUTONOMOUS MARINE REASONING SYSTEM</span>
          </div>
        </div>

        {/* 2. Headline in Untitled Serif at Weight 400 Strictly (Never bold!) */}
        <h1
          style={{
            fontFamily: 'var(--font-untitled-serif), Georgia, serif',
            fontSize: 'clamp(2.5rem, 5.2vw, 4.8rem)',
            fontWeight: 400,
            color: '#242424',
            letterSpacing: '-0.02em',
            lineHeight: 1.15,
            maxWidth: '960px',
            margin: '0 auto 24px auto',
          }}
        >
          Bridging space, oceanography, and coastal operations through verifiable marine intelligence.
        </h1>

        {/* 3. Monospace Subtext at 20px Graphite (4e4d4d) */}
        <p
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: 'clamp(15px, 1.35vw, 19px)',
            color: '#4e4d4d',
            lineHeight: 1.45,
            maxWidth: '780px',
            margin: '0 auto 36px auto',
            letterSpacing: '-0.02em',
          }}
        >
          Synthesizing ISRO MOSDAC satellite passes, INCOIS ocean circulation models, IMD cyclone vectors, and coastal AIS radar into deterministically reasoned maritime decisions.
        </p>

        {/* 4. Action Button Pair (Lake Blue 100px Pill + Ghost 100px Pill) */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px',
            flexWrap: 'wrap',
            marginBottom: '64px',
          }}
        >
          {/* Primary Pill Button (Blue) - Single primary action */}
          <a
            href="#portals"
            className="btn-monad-blue"
            style={{
              backgroundColor: '#2b59d1',
              color: '#ffffff',
              borderRadius: '100px',
              padding: '16px 32px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '14px',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'opacity 0.15s ease',
            }}
          >
            <span>ENTER WORKSPACE</span>
            <span style={{ fontSize: '13px' }}>▸</span>
          </a>

          {/* Ghost Pill Button - Secondary conversion action */}
          <a
            href="#architecture"
            className="btn-monad-ghost"
            style={{
              backgroundColor: 'transparent',
              color: '#242424',
              border: '1px solid #242424',
              borderRadius: '100px',
              padding: '16px 32px',
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '14px',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              transition: 'background-color 0.15s ease',
            }}
          >
            DATA PIPELINE
          </a>
        </div>

        {/* 5. Monad Live Telemetry Card (40px border-radius, 1px Ash border) */}
        <div
          className="monad-card"
          style={{
            width: '100%',
            maxWidth: '1020px',
            margin: '0 auto',
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '32px 40px',
            textAlign: 'left',
          }}
        >
          {/* Header Row */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: '1px solid #cecac8',
              paddingBottom: '16px',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#2b59d1',
                }}
              />
              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                  fontSize: '20px',
                  fontWeight: 400,
                  color: '#242424',
                  letterSpacing: '-0.02em',
                }}
              >
                Operational Telemetry Stream
              </span>
            </div>

            <div
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '12px',
                color: '#797776',
                letterSpacing: '-0.02em',
                textTransform: 'uppercase',
              }}
            >
              SECTOR: 12.91°N, 74.85°E • KARNATAKA COASTAL
            </div>
          </div>

          {/* Telemetry Cells */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '16px',
            }}
          >
            {/* Cell 1: Multi-Agent Engine */}
            <div
              style={{
                padding: '16px 20px',
                backgroundColor: 'rgba(207, 218, 245, 0.4)',
                border: '1px solid #cecac8',
                borderRadius: '24px',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '11px',
                  color: '#797776',
                  textTransform: 'uppercase',
                  letterSpacing: '-0.02em',
                  marginBottom: '4px',
                }}
              >
                DECISION ENGINE
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '14px',
                  color: '#242424',
                  fontWeight: 500,
                }}
              >
                6 Multi-Agent Swarm Active
              </div>
            </div>

            {/* Cell 2: Atmospheric Gradient */}
            <div
              style={{
                padding: '16px 20px',
                backgroundColor: 'rgba(255, 148, 115, 0.15)',
                border: '1px solid #cecac8',
                borderRadius: '24px',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '11px',
                  color: '#797776',
                  textTransform: 'uppercase',
                  letterSpacing: '-0.02em',
                  marginBottom: '4px',
                }}
              >
                SWELL TRACKER
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '14px',
                  color: '#242424',
                  fontWeight: 500,
                }}
              >
                TEJ Track • Gale Buffer 150 km
              </div>
            </div>

            {/* Cell 3: Satellite */}
            <div
              style={{
                padding: '16px 20px',
                backgroundColor: 'rgba(167, 252, 205, 0.2)',
                border: '1px solid #cecac8',
                borderRadius: '24px',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '11px',
                  color: '#797776',
                  textTransform: 'uppercase',
                  letterSpacing: '-0.02em',
                  marginBottom: '4px',
                }}
              >
                SATELLITE PASS
              </div>
              <div
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '14px',
                  color: '#242424',
                  fontWeight: 500,
                }}
              >
                Oceansat-3 OCM (06:40 UTC)
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
