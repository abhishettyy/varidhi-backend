'use client';

import React from 'react';
import { Database, Cpu, Navigation, ShieldAlert, Layers, Activity } from 'lucide-react';

export const AboutSection: React.FC = () => {
  return (
    <section
      id="about"
      style={{
        width: '100%',
        padding: '80px 24px',
        backgroundColor: '#f5f5f5',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        borderBottom: '1px solid rgba(39, 39, 42, 0.09)',
      }}
    >
      <div style={{ maxWidth: '1000px', width: '100%', textAlign: 'center' }}>
        {/* Section Pill */}
        <span
          style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            letterSpacing: '0.08em',
            color: '#797267',
            textTransform: 'uppercase',
            display: 'inline-block',
            marginBottom: '12px',
          }}
        >
          ABOUT VARIDHI
        </span>

        <h2
          style={{
            fontSize: 'clamp(1.8rem, 3.2vw, 2.6rem)',
            fontWeight: 800,
            color: '#221f1c',
            fontFamily: 'var(--font-editorial, serif)',
            letterSpacing: '0.02em',
            marginBottom: '20px',
            lineHeight: 1.2,
          }}
        >
          Unified Marine Intelligence
        </h2>

        <p
          style={{
            fontSize: '1.05rem',
            color: '#797267',
            maxWidth: '780px',
            margin: '0 auto 48px auto',
            lineHeight: 1.6,
          }}
        >
          Varidhi brings together marine observations, weather, geospatial information,
          safety intelligence and AI into one coherent decision-support platform.
        </p>

        {/* Three Core Pillars */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '24px',
            textAlign: 'left',
          }}
        >
          {/* Pillar 1: DATA */}
          <div
            className="micro-card"
            style={{
              padding: '32px 24px',
              backgroundColor: '#ffffff',
              border: '1px solid rgba(39, 39, 42, 0.09)',
              borderRadius: '18px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)',
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '8px',
                backgroundColor: '#f5f5f5',
                border: '1px solid rgba(39, 39, 42, 0.09)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#518bdb',
                marginBottom: '20px',
              }}
            >
              <Database size={22} />
            </div>
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#797267',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              PILLAR 01
            </span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#221f1c', margin: '6px 0 10px 0', fontFamily: 'var(--font-editorial, serif)' }}>
              DATA
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#797267', lineHeight: 1.55 }}>
              Marine observations, ocean weather, INCOIS PFZ forecasts, and geospatial boundaries
              aggregated into a single verifiable layer.
            </p>
          </div>

          {/* Pillar 2: INTELLIGENCE */}
          <div
            className="micro-card"
            style={{
              padding: '32px 24px',
              backgroundColor: '#ffffff',
              border: '1px solid rgba(39, 39, 42, 0.09)',
              borderRadius: '18px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)',
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '8px',
                backgroundColor: '#f5f5f5',
                border: '1px solid rgba(39, 39, 42, 0.09)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#36bab8',
                marginBottom: '20px',
              }}
            >
              <Cpu size={22} />
            </div>
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#797267',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              PILLAR 02
            </span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#221f1c', margin: '6px 0 10px 0', fontFamily: 'var(--font-editorial, serif)' }}>
              INTELLIGENCE
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#797267', lineHeight: 1.55 }}>
              AI-assisted natural-language decision support. The system answers your questions
              by interrogating deterministic ocean analytics without hallucinating.
            </p>
          </div>

          {/* Pillar 3: ACTION */}
          <div
            className="micro-card"
            style={{
              padding: '32px 24px',
              backgroundColor: '#ffffff',
              border: '1px solid rgba(39, 39, 42, 0.09)',
              borderRadius: '18px',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)',
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '8px',
                backgroundColor: '#f5f5f5',
                border: '1px solid rgba(39, 39, 42, 0.09)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#221f1c',
                marginBottom: '20px',
              }}
            >
              <Navigation size={22} />
            </div>
            <span
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#797267',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              PILLAR 03
            </span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#221f1c', margin: '6px 0 10px 0', fontFamily: 'var(--font-editorial, serif)' }}>
              ACTION
            </h3>
            <p style={{ fontSize: '0.9rem', color: '#797267', lineHeight: 1.55 }}>
              Actionable zone recommendations, maritime safety warnings, legal boundary compliance,
              and interactive geospatial evidence on the map.
            </p>
          </div>
        </div>

        {/* How It Works Subsection */}
        <div
          id="how-it-works"
          style={{
            marginTop: '80px',
            paddingTop: '60px',
            borderTop: '1px solid rgba(39, 39, 42, 0.09)',
          }}
        >
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.08em',
              color: '#797267',
              textTransform: 'uppercase',
              display: 'inline-block',
              marginBottom: '10px',
            }}
          >
            ARCHITECTURE FLOW
          </span>
          <h3 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#221f1c', marginBottom: '28px', fontFamily: 'var(--font-editorial, serif)' }}>
            From Natural Language to Confirmed Marine Action
          </h3>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexWrap: 'wrap',
              gap: '12px',
              fontSize: '0.85rem',
              color: '#221f1c',
            }}
          >
            <div className="micro-card" style={{ padding: '10px 18px', backgroundColor: '#ffffff', border: '1px solid rgba(39, 39, 42, 0.09)', borderRadius: '8px', color: '#221f1c', fontWeight: 600 }}>
              💬 Natural Language Query
            </div>
            <span style={{ color: '#797267', fontWeight: 800 }}>→</span>
            <div className="micro-card" style={{ padding: '10px 18px', backgroundColor: '#ffffff', border: '1px solid rgba(39, 39, 42, 0.09)', borderRadius: '8px', color: '#221f1c', fontWeight: 600 }}>
              🤖 Varidhi AI Orchestrator
            </div>
            <span style={{ color: '#797267', fontWeight: 800 }}>→</span>
            <div className="micro-card" style={{ padding: '10px 18px', backgroundColor: '#ffffff', border: '1px solid rgba(39, 39, 42, 0.09)', borderRadius: '8px', color: '#221f1c', fontWeight: 600 }}>
              🛰️ Marine + Oceanographic Engines
            </div>
            <span style={{ color: '#797267', fontWeight: 800 }}>→</span>
            <div className="micro-card" style={{ padding: '10px 18px', backgroundColor: '#ffffff', border: '1px solid rgba(39, 39, 42, 0.09)', borderRadius: '8px', color: '#221f1c', fontWeight: 600 }}>
              ⚖️ Safety & Legal Verification
            </div>
            <span style={{ color: '#797267', fontWeight: 800 }}>→</span>
            <div className="micro-card" style={{ padding: '10px 18px', backgroundColor: '#cbfbf1', border: '1px solid rgba(39, 39, 42, 0.09)', borderRadius: '8px', color: '#221f1c', fontWeight: 700 }}>
              🗺️ Map + Clear Recommendation
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
