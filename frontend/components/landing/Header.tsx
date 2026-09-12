'use client';

import React from 'react';
import Link from 'next/link';

export const Header: React.FC = () => {
  return (
    <header
      style={{
        width: '100%',
        height: '80px',
        backgroundColor: '#f6f3f1',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 clamp(20px, 5vw, 64px)',
        zIndex: 100,
        position: 'sticky',
        top: 0,
      }}
    >
      {/* Brand Identity - Left: Monad wordmark + circular dot mark */}
      <Link
        href="/"
        style={{
          textDecoration: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}
      >
        <span
          style={{
            fontFamily: 'var(--font-untitled-serif), Georgia, serif',
            fontSize: '1.65rem',
            fontWeight: 400,
            letterSpacing: '-0.02em',
            color: '#242424',
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
            display: 'inline-block',
          }}
        />
        <span
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '11px',
            color: '#797776',
            letterSpacing: '-0.02em',
            textTransform: 'uppercase',
            marginLeft: '4px',
          }}
        >
          [ISRO SIH 26176]
        </span>
      </Link>

      {/* Navigation Links - Center (ABC Diatype Mono Uppercase) */}
      <nav
        style={{
          display: 'none',
          alignItems: 'center',
          gap: '28px',
        }}
        className="monad-nav-desktop"
      >
        <a
          href="#portals"
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '14px',
            fontWeight: 500,
            color: '#242424',
            textDecoration: 'none',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#242424')}
        >
          PORTALS
        </a>

        <a
          href="#problem"
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '14px',
            fontWeight: 500,
            color: '#242424',
            textDecoration: 'none',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#242424')}
        >
          PARADOX
        </a>

        <a
          href="#architecture"
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '14px',
            fontWeight: 500,
            color: '#242424',
            textDecoration: 'none',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#242424')}
        >
          PIPELINE
        </a>

        <a
          href="#metrics"
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '14px',
            fontWeight: 500,
            color: '#242424',
            textDecoration: 'none',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#242424')}
        >
          ANALYTICS
        </a>

        <a
          href="#references"
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '14px',
            fontWeight: 500,
            color: '#242424',
            textDecoration: 'none',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#2b59d1')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#242424')}
        >
          SOURCES
        </a>
      </nav>

      {/* Action Buttons Right - Ghost + Lake Blue Pill */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link
          href="/researcher"
          style={{
            backgroundColor: 'transparent',
            color: '#242424',
            border: '1px solid #242424',
            borderRadius: '100px',
            padding: '10px 20px',
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '13px',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(36, 36, 36, 0.06)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          RESEARCH GIS
        </Link>

        <Link
          href="#portals"
          style={{
            backgroundColor: '#2b59d1',
            color: '#ffffff',
            border: 'none',
            borderRadius: '100px',
            padding: '10px 22px',
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '13px',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'opacity 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.92')}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
        >
          <span>SELECT PORTAL</span>
          <span style={{ fontSize: '11px' }}>▸</span>
        </Link>
      </div>

      <style jsx>{`
        @media (min-width: 960px) {
          .monad-nav-desktop {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  );
};
