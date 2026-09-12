'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { RecommendationCard } from '@/components/fisherman/RecommendationCard';
import { AlternativeZoneCard } from '@/components/fisherman/AlternativeZoneCard';
import { WhyRecommendation } from '@/components/fisherman/WhyRecommendation';
import { getMockZones } from '@/services/api/mockData';

export default function FishermanRecommendationPage() {
  const zones = getMockZones();
  const recommendedZone = zones.find((z) => z.id === 'ZONE_B') || zones[0];
  const alternativeZones = zones.filter((z) => z.id !== 'ZONE_B');

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
            DECISION ENGINE OUTPUT
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
            Harvest Ground Recommendations
          </h1>
        </div>

        <RecommendationCard zone={recommendedZone} />

        <WhyRecommendation zone={recommendedZone} />

        <div style={{ marginTop: '14px' }}>
          <h2
            style={{
              fontSize: '1.25rem',
              fontWeight: 400,
              color: '#242424',
              marginBottom: '12px',
              fontFamily: 'var(--font-untitled-serif), serif',
              letterSpacing: '-0.02em',
            }}
          >
            Alternative & Disqualified Candidate Zones
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {alternativeZones.map((z) => (
              <AlternativeZoneCard key={z.id} zone={z} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
