'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, RefreshCw, Radio } from 'lucide-react';

interface AuthorityHeaderProps {
  onRefresh?: () => void;
  activeAlertsCount?: number;
}

export const AuthorityHeader: React.FC<AuthorityHeaderProps> = ({
  onRefresh,
  activeAlertsCount = 3,
}) => {
  return (
    <header
      style={{
        height: '60px',
        padding: '0 24px',
        backgroundColor: '#f6f3f1',
        borderBottom: '1px solid #cecac8',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 100,
        position: 'relative',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Left Brand & Persona */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <Link
          href="/"
          title="Return to Main Portal"
          style={{
            color: '#242424',
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
            padding: '6px 12px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            fontSize: '11px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            gap: '6px',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#cfdaf5';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#ffffff';
          }}
        >
          <ArrowLeft size={13} />
          <span>PORTAL</span>
        </Link>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span
              style={{
                fontFamily: 'var(--font-untitled-serif), serif',
                fontSize: '1.25rem',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
              }}
            >
              Varidhi
            </span>
            <span
              style={{
                fontSize: '10px',
                padding: '2px 8px',
                borderRadius: '9999px',
                backgroundColor: '#cfdaf5',
                color: '#2b59d1',
                border: '1px solid #cecac8',
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}
            >
              MARINE SURVEILLANCE
            </span>
          </div>
          <p style={{ fontSize: '10px', color: '#767371', margin: 0, marginTop: '2px' }}>
            Karnataka Coastal Zone • Maritime Enforcement & Hazard Response
          </p>
        </div>
      </div>

      {/* Right Telemetry Indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 12px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            fontSize: '11px',
            color: '#242424',
            fontWeight: 500,
          }}
        >
          <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#2b59d1' }} />
          <span>SURVEILLANCE ACTIVE</span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 12px',
            borderRadius: '100px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            fontSize: '11px',
          }}
        >
          <span style={{ color: '#767371', textTransform: 'uppercase', fontSize: '10px' }}>ALERTS:</span>
          <span
            style={{
              color: '#ff9473',
              fontWeight: 600,
            }}
          >
            {activeAlertsCount} ACTIVE
          </span>
        </div>

        <Link
          href="/researcher"
          style={{
            fontSize: '11px',
            color: '#242424',
            textDecoration: 'none',
            padding: '6px 14px',
            borderRadius: '100px',
            border: '1px solid #cecac8',
            backgroundColor: '#ffffff',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#cfdaf5';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#ffffff';
          }}
        >
          <span>RESEARCH VIEW</span>
        </Link>
      </div>
    </header>
  );
};
