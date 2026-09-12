'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { X } from 'lucide-react';

export const AnnouncementBar: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <div
      style={{
        width: '100%',
        minHeight: '40px',
        backgroundColor: '#000000',
        color: '#f6f3f1',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 20px',
        fontSize: '13px',
        fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
        letterSpacing: '-0.02em',
        position: 'relative',
        zIndex: 101,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap',
          justifyContent: 'center',
        }}
      >
        <span>
          VARIDHI v2.4 • INCOIS PFZ REAL-TIME TELEMETRY FEED OPERATIONAL
        </span>

        <Link
          href="#portals"
          style={{
            padding: '3px 10px',
            borderRadius: '9999px',
            border: '1px solid #f6f3f1',
            color: '#f6f3f1',
            fontSize: '11px',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#f6f3f1';
            e.currentTarget.style.color = '#000000';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = '#f6f3f1';
          }}
        >
          EXPLORE PORTALS
        </Link>
      </div>

      <button
        type="button"
        onClick={() => setIsVisible(false)}
        aria-label="Close notification"
        style={{
          position: 'absolute',
          right: '16px',
          background: 'none',
          border: 'none',
          color: '#f6f3f1',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          padding: '4px',
          opacity: 0.8,
          transition: 'opacity 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.8')}
      >
        <X size={16} />
      </button>
    </div>
  );
};
