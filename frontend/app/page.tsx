'use client';

import React from 'react';
import { AnnouncementBar } from '@/components/landing/AnnouncementBar';
import { Header } from '@/components/landing/Header';
import { Hero } from '@/components/landing/Hero';
import { PortalsSection } from '@/components/landing/PortalsSection';
import { ProblemSection } from '@/components/landing/ProblemSection';
import { ArchitectureSection } from '@/components/landing/ArchitectureSection';
import { MetricsSection } from '@/components/landing/MetricsSection';
import { Footer } from '@/components/landing/Footer';

export default function LandingPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        width: '100%',
        backgroundColor: '#f6f3f1',
        color: '#242424',
        display: 'flex',
        flexDirection: 'column',
        overflowX: 'hidden',
        fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
      }}
    >
      {/* 0. Monad Top Black Announcement Bar */}
      <AnnouncementBar />

      {/* 1. Monad Nav Header */}
      <Header />

      <main style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* 2. Monad Hero Section */}
        <Hero />

        {/* 3. Role Portals Grid */}
        <PortalsSection />

        {/* 4. The Core Challenge: Marine Data Paradox */}
        <ProblemSection />

        {/* 5. Monad Data Pipeline Diagram */}
        <ArchitectureSection />

        {/* 6. Empirical Impact & Latency Charts */}
        <MetricsSection />
      </main>

      {/* 7. Monad Footer */}
      <Footer />
    </div>
  );
}
