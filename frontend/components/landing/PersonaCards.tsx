'use client';

import React from 'react';
import Link from 'next/link';
import {
  Fish,
  Shield,
  Compass,
  ArrowRight,
  ShieldCheck,
  Radio,
  Layers,
  Waves,
  Eye,
  AlertTriangle,
  TrendingUp,
} from 'lucide-react';

export const PersonaCards: React.FC = () => {
  return (
    <section
      id="explore"
      style={{
        width: '100%',
        padding: '90px 24px 100px 24px',
        backgroundColor: '#040814',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
      }}
    >
      <div style={{ maxWidth: '1240px', width: '100%' }}>
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: '56px' }}>
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 800,
              letterSpacing: '0.12em',
              color: '#00e5ff',
              textTransform: 'uppercase',
              display: 'inline-block',
              marginBottom: '12px',
            }}
          >
            EXPLORE VARIDHI
          </span>
          <h2
            style={{
              fontSize: 'clamp(2rem, 3.5vw, 2.8rem)',
              fontWeight: 900,
              color: '#ffffff',
              letterSpacing: '-0.02em',
              marginBottom: '14px',
            }}
          >
            Choose the Workspace That Matches Your Role
          </h2>
          <p
            style={{
              fontSize: '1.05rem',
              color: '#94a3b8',
              maxWidth: '640px',
              margin: '0 auto',
              lineHeight: 1.5,
            }}
          >
            Tailored decision-support experiences powered by the same underlying oceanographic intelligence.
          </p>
        </div>

        {/* Three Large Featured Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: '28px',
          }}
        >
          {/* Card 1: FISHERMAN */}
          <div className="persona-card persona-card-fisherman">
            {/* Visual Header / Graphic Banner */}
            <div
              style={{
                height: '190px',
                width: '100%',
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(6, 78, 59, 0.4) 100%), #061726',
                borderBottom: '1px solid rgba(16, 185, 129, 0.3)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Decorative Graphic Element */}
              <div
                style={{
                  position: 'absolute',
                  right: '-20px',
                  bottom: '-20px',
                  opacity: 0.15,
                  color: '#10b981',
                }}
              >
                <Fish size={180} />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 1 }}>
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: '10px',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    border: '1.5px solid #10b981',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#34d399',
                  }}
                >
                  <Fish size={24} />
                </div>
                <span
                  style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    color: '#34d399',
                    fontWeight: 800,
                    border: '1px solid rgba(16, 185, 129, 0.4)',
                    letterSpacing: '0.04em',
                  }}
                >
                  FIELD USER
                </span>
              </div>

              <div style={{ zIndex: 1 }}>
                <span style={{ fontSize: '0.75rem', color: '#6ee7b7', fontWeight: 700, textTransform: 'uppercase' }}>
                  PERSONA 01
                </span>
                <h3 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#ffffff', lineHeight: 1.15 }}>
                  Fisherman
                </h3>
              </div>
            </div>

            {/* Content Body */}
            <div style={{ padding: '26px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <p style={{ fontSize: '0.96rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px' }}>
                  Find better fishing zones, understand sea conditions and stay aware of safety and marine restrictions.
                </p>

                {/* Key Highlights */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '28px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <ShieldCheck size={16} color="#10b981" />
                    <span>Action-oriented zone recommendations (Zone B: 31 km)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <Waves size={16} color="#38bdf8" />
                    <span>Plain-language sea condition & safety checks</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <Shield size={16} color="#818cf8" />
                    <span>Protected marine sanctuary boundary alerts</span>
                  </div>
                </div>
              </div>

              {/* Action Link */}
              <Link
                href="/fisherman"
                className="btn-marine"
                style={{
                  textDecoration: 'none',
                  justifyContent: 'center',
                  padding: '12px 20px',
                  fontSize: '0.92rem',
                  fontWeight: 700,
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  borderColor: '#10b981',
                  color: '#34d399',
                  borderRadius: '8px',
                }}
              >
                <span>Enter Fisherman Workspace</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>

          {/* Card 2: MARINE AUTHORITY */}
          <div className="persona-card persona-card-authority">
            {/* Visual Header / Graphic Banner */}
            <div
              style={{
                height: '190px',
                width: '100%',
                background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(120, 53, 15, 0.4) 100%), #1f160a',
                borderBottom: '1px solid rgba(245, 158, 11, 0.3)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Decorative Graphic Element */}
              <div
                style={{
                  position: 'absolute',
                  right: '-20px',
                  bottom: '-20px',
                  opacity: 0.15,
                  color: '#f59e0b',
                }}
              >
                <Shield size={180} />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 1 }}>
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: '10px',
                    backgroundColor: 'rgba(245, 158, 11, 0.2)',
                    border: '1.5px solid #f59e0b',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fbbf24',
                  }}
                >
                  <Radio size={24} />
                </div>
                <span
                  style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(245, 158, 11, 0.2)',
                    color: '#fbbf24',
                    fontWeight: 800,
                    border: '1px solid rgba(245, 158, 11, 0.4)',
                    letterSpacing: '0.04em',
                  }}
                >
                  OPERATIONAL
                </span>
              </div>

              <div style={{ zIndex: 1 }}>
                <span style={{ fontSize: '0.75rem', color: '#fcd34d', fontWeight: 700, textTransform: 'uppercase' }}>
                  PERSONA 02
                </span>
                <h3 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#ffffff', lineHeight: 1.15 }}>
                  Marine Authority
                </h3>
              </div>
            </div>

            {/* Content Body */}
            <div style={{ padding: '26px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <p style={{ fontSize: '0.96rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px' }}>
                  Monitor marine conditions, fishing activity, hazards, restricted areas and emerging risks across your operational region.
                </p>

                {/* Key Highlights */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '28px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <Eye size={16} color="#f59e0b" />
                    <span>Regional surveillance & active fleet vessel tracking</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <AlertTriangle size={16} color="#f87171" />
                    <span>Critical alerts: High wind, storm buffer & incursions</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <Radio size={16} color="#fbbf24" />
                    <span>Broadcast safety advisories & fleet compliance stats</span>
                  </div>
                </div>
              </div>

              {/* Action Link */}
              <Link
                href="/authority"
                className="btn-marine"
                style={{
                  textDecoration: 'none',
                  justifyContent: 'center',
                  padding: '12px 20px',
                  fontSize: '0.92rem',
                  fontWeight: 700,
                  backgroundColor: 'rgba(245, 158, 11, 0.15)',
                  borderColor: '#f59e0b',
                  color: '#fbbf24',
                  borderRadius: '8px',
                }}
              >
                <span>Enter Authority Workspace</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>

          {/* Card 3: MARINE RESEARCHER */}
          <div className="persona-card persona-card-researcher">
            {/* Visual Header / Graphic Banner */}
            <div
              style={{
                height: '190px',
                width: '100%',
                background: 'linear-gradient(135deg, rgba(0, 229, 255, 0.25) 0%, rgba(8, 47, 73, 0.4) 100%), #05192d',
                borderBottom: '1px solid rgba(0, 229, 255, 0.3)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Decorative Graphic Element */}
              <div
                style={{
                  position: 'absolute',
                  right: '-20px',
                  bottom: '-20px',
                  opacity: 0.15,
                  color: '#00e5ff',
                }}
              >
                <Compass size={180} />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', zIndex: 1 }}>
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: '10px',
                    backgroundColor: 'rgba(0, 229, 255, 0.2)',
                    border: '1.5px solid #00e5ff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#00e5ff',
                  }}
                >
                  <Compass size={24} />
                </div>
                <span
                  style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(0, 229, 255, 0.2)',
                    color: '#00e5ff',
                    fontWeight: 800,
                    border: '1px solid rgba(0, 229, 255, 0.4)',
                    letterSpacing: '0.04em',
                  }}
                >
                  ANALYTICAL
                </span>
              </div>

              <div style={{ zIndex: 1 }}>
                <span style={{ fontSize: '0.75rem', color: '#7dd3fc', fontWeight: 700, textTransform: 'uppercase' }}>
                  PERSONA 03
                </span>
                <h3 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#ffffff', lineHeight: 1.15 }}>
                  Marine Researcher
                </h3>
              </div>
            </div>

            {/* Content Body */}
            <div style={{ padding: '26px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <p style={{ fontSize: '0.96rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '20px' }}>
                  Explore PFZs, SST, chlorophyll, marine conditions and historical ocean patterns through an analytical geospatial workspace.
                </p>

                {/* Key Highlights */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '28px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <Layers size={16} color="#00e5ff" />
                    <span>Multi-layer GIS: PFZ Fronts, SST deltas, Chlorophyll</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <TrendingUp size={16} color="#34d399" />
                    <span>Temporal time-slider (7-day hindcast & 48h forecast)</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#94a3b8' }}>
                    <Radio size={16} color="#818cf8" />
                    <span>Biophysical parameter tables & scientific evidence</span>
                  </div>
                </div>
              </div>

              {/* Action Link */}
              <Link
                href="/researcher"
                className="btn-marine"
                style={{
                  textDecoration: 'none',
                  justifyContent: 'center',
                  padding: '12px 20px',
                  fontSize: '0.92rem',
                  fontWeight: 700,
                  backgroundColor: 'rgba(0, 229, 255, 0.15)',
                  borderColor: '#00e5ff',
                  color: '#00e5ff',
                  borderRadius: '8px',
                }}
              >
                <span>Enter Researcher Workspace</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
