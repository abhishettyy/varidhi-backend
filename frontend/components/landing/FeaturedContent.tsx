'use client';

import React from 'react';
import Link from 'next/link';

export const FeaturedContent: React.FC = () => {
  const cards = [
    {
      id: 'fisherman',
      image: '/images/card_fisherman.jpg',
      title: 'OceanReports // Fisherman',
      description:
        'This web-based, report-centric tool provides coastal and ocean fishermen with high-level analysis, catch opportunities, and maritime safety alerts.',
      buttonText: 'Launch',
      href: '/fisherman',
    },
    {
      id: 'vessel-traffic',
      image: '/images/card_authority.jpg',
      title: 'Vessel Traffic // Authority',
      description:
        'Download and view AIS surveillance data, monitor vessel traffic density, enforce marine sanctuaries, and track emerging storm hazards.',
      buttonText: 'Learn More',
      href: '/authority',
    },
    {
      id: 'national-viewer',
      image: '/images/card_researcher.png',
      title: 'National Viewer // Researcher',
      description:
        'Use the National Viewer to view and interact with multi-layer oceanographic data, INCOIS PFZ forecasts, and ocean temperature gradients.',
      buttonText: 'Launch',
      href: '/researcher',
    },
  ];

  return (
    <section
      style={{
        width: '100%',
        backgroundColor: '#ffffff',
        padding: '10px clamp(16px, 5vw, 64px) 80px clamp(16px, 5vw, 64px)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <div style={{ maxWidth: '1280px', width: '100%' }}>
        {/* Section Heading - Matching Marine Cadastre Screenshot */}
        <h2
          style={{
            fontSize: '1.85rem',
            fontWeight: 800,
            color: '#1e293b',
            marginBottom: '28px',
            letterSpacing: '-0.02em',
          }}
        >
          Featured Content
        </h2>

        {/* 3 Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '28px',
          }}
        >
          {cards.map((card) => (
            <div
              key={card.id}
              style={{
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '24px',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.08)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'none';
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
              }}
            >
              {/* Card Top Visual Preview */}
              <div
                style={{
                  width: '100%',
                  height: '240px',
                  position: 'relative',
                  backgroundColor: '#f1f5f9',
                  overflow: 'hidden',
                }}
              >
                <img
                  src={card.image}
                  alt={card.title}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
              </div>

              {/* Card Content Body */}
              <div
                style={{
                  padding: '24px 24px 28px 24px',
                  display: 'flex',
                  flexDirection: 'column',
                  flex: 1,
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <h3
                    style={{
                      fontSize: '1.35rem',
                      fontWeight: 800,
                      color: '#1e293b',
                      marginBottom: '12px',
                    }}
                  >
                    {card.title}
                  </h3>
                  <p
                    style={{
                      fontSize: '0.94rem',
                      color: '#475569',
                      lineHeight: 1.5,
                      marginBottom: '28px',
                    }}
                  >
                    {card.description}
                  </p>
                </div>

                {/* Dark Rounded Pill Button (Exact Marine Cadastre Style) */}
                <Link
                  href={card.href}
                  style={{
                    display: 'block',
                    width: '100%',
                    padding: '13px 20px',
                    backgroundColor: '#3f3f46',
                    color: '#ffffff',
                    textAlign: 'center',
                    borderRadius: '28px',
                    fontSize: '0.98rem',
                    fontWeight: 600,
                    textDecoration: 'none',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#18181b')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#3f3f46')}
                >
                  {card.buttonText}
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
