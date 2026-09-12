'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { SafetyCard } from '@/components/fisherman/SafetyCard';
import { SeaConditions } from '@/components/fisherman/SeaConditions';

export default function FishermanSafetyPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f6f3f1',
        color: '#242424',
        padding: '36px 20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ maxWidth: '680px', width: '100%', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <Link
          href="/fisherman"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            color: '#242424',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            padding: '7px 16px',
            borderRadius: '100px',
            textDecoration: 'none',
            fontSize: '11px',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            alignSelf: 'flex-start',
            transition: 'background-color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
        >
          <ArrowLeft size={13} />
          <span>RETURN TO WORKSPACE</span>
        </Link>

        <div>
          <span style={{ fontSize: '10px', color: '#767371', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            HYDRODYNAMIC ASSESSMENT
          </span>
          <h1
            style={{
              fontSize: '2rem',
              fontWeight: 400,
              color: '#242424',
              fontFamily: 'var(--font-untitled-serif), serif',
              letterSpacing: '-0.02em',
              margin: '4px 0 0 0',
            }}
          >
            Marine Safety & Coastal Conditions
          </h1>
        </div>

        <SafetyCard />
        <SeaConditions />
      </div>
    </div>
  );
}
