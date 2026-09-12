'use client';

import React from 'react';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer
      id="references"
      style={{
        width: '100%',
        backgroundColor: '#f6f3f1',
        color: '#242424',
        borderTop: '1px solid #cecac8',
        padding: '72px clamp(24px, 5vw, 64px) 40px clamp(24px, 5vw, 64px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '1280px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '48px',
          marginBottom: '56px',
        }}
      >
        {/* Col 1: Brand & Theme */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <span
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '1.75rem',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
              }}
            >
              VARIDHI
            </span>
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#2b59d1',
              }}
            />
          </div>
          <p
            style={{
              fontSize: '13px',
              color: '#4e4d4d',
              lineHeight: 1.5,
              marginBottom: '20px',
              letterSpacing: '-0.02em',
            }}
          >
            Autonomous Marine Reasoning with Multi-Agent Swarm Synthesis. Developed for Smart India Hackathon under ISRO Theme: Disaster Management.
          </p>
          <div
            className="monad-node-tag"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '9999px',
              backgroundColor: '#f6f3f1',
              border: '1px solid #cecac8',
              color: '#242424',
              fontSize: '11px',
              letterSpacing: '-0.02em',
              textTransform: 'uppercase',
            }}
          >
            <Sparkles size={12} color="#2b59d1" />
            PROBLEM STATEMENT: SIH 26176
          </div>
        </div>

        {/* Col 2: Operational Portals */}
        <div>
          <h4
            style={{
              fontSize: '12px',
              fontWeight: 500,
              color: '#242424',
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              marginBottom: '18px',
            }}
          >
            OPERATIONAL WORKSPACES
          </h4>
          <ul
            style={{
              listStyle: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              fontSize: '13px',
              letterSpacing: '-0.02em',
            }}
          >
            <li>
              <Link
                href="/fisherman"
                style={{ color: '#4e4d4d', textDecoration: 'none', transition: 'color 0.15s' }}
                onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
                onMouseLeave={(e) => (e.currentTarget.style.color = '#4e4d4d')}
              >
                Fishermen Portal (Safety & PFZ) →
              </Link>
            </li>
            <li>
              <Link
                href="/authority"
                style={{ color: '#4e4d4d', textDecoration: 'none', transition: 'color 0.15s' }}
                onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
                onMouseLeave={(e) => (e.currentTarget.style.color = '#4e4d4d')}
              >
                Disaster Command (Surveillance) →
              </Link>
            </li>
            <li>
              <Link
                href="/researcher"
                style={{ color: '#4e4d4d', textDecoration: 'none', transition: 'color 0.15s' }}
                onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
                onMouseLeave={(e) => (e.currentTarget.style.color = '#4e4d4d')}
              >
                Researcher Portal (Multi-Sensor GIS) →
              </Link>
            </li>
          </ul>
        </div>

        {/* Col 3: Data Provenance & Academic References */}
        <div>
          <h4
            style={{
              fontSize: '12px',
              fontWeight: 500,
              color: '#242424',
              textTransform: 'uppercase',
              letterSpacing: '-0.02em',
              marginBottom: '18px',
            }}
          >
            AUTHORITATIVE FEEDS
          </h4>
          <ul
            style={{
              listStyle: 'none',
              padding: 0,
              margin: 0,
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              fontSize: '13px',
              letterSpacing: '-0.02em',
            }}
          >
            <li style={{ color: '#4e4d4d' }}>
              <span style={{ color: '#242424', fontWeight: 500 }}>ISRO MOSDAC:</span> INSAT-3DR SST & Oceansat-3 OCM
            </li>
            <li style={{ color: '#4e4d4d' }}>
              <span style={{ color: '#242424', fontWeight: 500 }}>INCOIS:</span> PFZ Bulletins & Wave Forecasts
            </li>
            <li style={{ color: '#4e4d4d' }}>
              <span style={{ color: '#242424', fontWeight: 500 }}>IMD RSMC:</span> Cyclone Track Projections
            </li>
            <li style={{ color: '#4e4d4d' }}>
              <span style={{ color: '#242424', fontWeight: 500 }}>AISHub / ICG:</span> Real-time Coastal Vessels
            </li>
          </ul>
        </div>
      </div>

      {/* Bottom Bar */}
      <div
        style={{
          width: '100%',
          maxWidth: '1280px',
          borderTop: '1px solid #cecac8',
          paddingTop: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '12px',
          color: '#797776',
          letterSpacing: '-0.02em',
        }}
      >
        <div>© 2026 Team Varidhi. Built for ISRO Smart India Hackathon (SIH 26176).</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <span>Theme: Disaster Management</span>
          <span>•</span>
          <span>Monad Editorial Tech Journal on Warm Parchment</span>
        </div>
      </div>
    </footer>
  );
};
