'use client';

import React from 'react';
import { LineChart, BarChart2 } from 'lucide-react';

export const MetricsSection: React.FC = () => {
  return (
    <section
      id="metrics"
      style={{
        width: '100%',
        backgroundColor: '#f6f3f1',
        padding: '80px 24px 104px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        position: 'relative',
      }}
    >
      {/* 1. Monad Node Pill Tag */}
      <div style={{ marginBottom: '20px' }}>
        <span
          className="monad-node-tag"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '9999px',
            padding: '10px 20px',
            fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
            fontSize: '12px',
            textTransform: 'uppercase',
            letterSpacing: '-0.02em',
            color: '#242424',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: '#2b59d1',
            }}
          />
          EMPIRICAL BENCHMARKS
        </span>
      </div>

      {/* 2. Section Heading in Untitled Serif at Weight 400 Strictly */}
      <h2
        style={{
          fontFamily: 'var(--font-untitled-serif), Georgia, serif',
          fontSize: 'clamp(2.2rem, 3.8vw, 3.2rem)',
          fontWeight: 400,
          color: '#242424',
          letterSpacing: '-0.02em',
          textAlign: 'center',
          margin: '0 0 16px 0',
          lineHeight: 1.2,
        }}
      >
        Validated Operational Impact & Latency
      </h2>

      {/* 3. Subtitle in ABC Diatype Mono */}
      <p
        style={{
          fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
          fontSize: 'clamp(14px, 1.2vw, 16px)',
          color: '#4e4d4d',
          lineHeight: 1.4,
          maxWidth: '800px',
          textAlign: 'center',
          margin: '0 auto 64px auto',
          letterSpacing: '-0.02em',
        }}
      >
        Benchmarking Varidhi&apos;s multi-agent reasoning across coastal safety latency, advisory accuracy, and oceanographic prediction.
      </p>

      {/* 4. Four Metric Cards (40px padding, 40px radius, 1px Ash border) */}
      <div
        style={{
          width: '100%',
          maxWidth: '1280px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '20px',
          marginBottom: '32px',
        }}
      >
        {/* Stat 1 */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '36px 32px',
            boxShadow: 'none',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-untitled-serif), Georgia, serif',
              fontSize: '44px',
              fontWeight: 400,
              color: '#2b59d1',
              lineHeight: 1,
              marginBottom: '12px',
              letterSpacing: '-0.02em',
            }}
          >
            &lt; 3.2s
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              color: '#242424',
              marginBottom: '6px',
              letterSpacing: '-0.02em',
            }}
          >
            Multi-Agent Synthesis
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              color: '#4e4d4d',
              lineHeight: 1.45,
              letterSpacing: '-0.02em',
            }}
          >
            Total end-to-end latency for 5-agent state graph query resolution.
          </div>
        </div>

        {/* Stat 2 */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '36px 32px',
            boxShadow: 'none',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-untitled-serif), Georgia, serif',
              fontSize: '44px',
              fontWeight: 400,
              color: '#242424',
              lineHeight: 1,
              marginBottom: '12px',
              letterSpacing: '-0.02em',
            }}
          >
            94.2%
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              color: '#242424',
              marginBottom: '6px',
              letterSpacing: '-0.02em',
            }}
          >
            PFZ Hit-Rate Correlation
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              color: '#4e4d4d',
              lineHeight: 1.45,
              letterSpacing: '-0.02em',
            }}
          >
            Match accuracy between OCM-3 chlorophyll plume edges and catch yields.
          </div>
        </div>

        {/* Stat 3 */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '36px 32px',
            boxShadow: 'none',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-untitled-serif), Georgia, serif',
              fontSize: '44px',
              fontWeight: 400,
              color: '#242424',
              lineHeight: 1,
              marginBottom: '12px',
              letterSpacing: '-0.02em',
            }}
          >
            150 km
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              color: '#242424',
              marginBottom: '6px',
              letterSpacing: '-0.02em',
            }}
          >
            Proactive Gale Buffer
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              color: '#4e4d4d',
              lineHeight: 1.45,
              letterSpacing: '-0.02em',
            }}
          >
            Automatic evacuation perimeter generated for cyclonic wind bands.
          </div>
        </div>

        {/* Stat 4 */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '36px 32px',
            boxShadow: 'none',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-untitled-serif), Georgia, serif',
              fontSize: '44px',
              fontWeight: 400,
              color: '#f37a0a',
              lineHeight: 1,
              marginBottom: '12px',
              letterSpacing: '-0.02em',
            }}
          >
            0
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              fontWeight: 500,
              textTransform: 'uppercase',
              color: '#242424',
              marginBottom: '6px',
              letterSpacing: '-0.02em',
            }}
          >
            Hallucinated Physics
          </div>
          <div
            style={{
              fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
              fontSize: '13px',
              color: '#4e4d4d',
              lineHeight: 1.45,
              letterSpacing: '-0.02em',
            }}
          >
            Deterministic rule engines verify wave heights and winds prior to LLM prose.
          </div>
        </div>
      </div>

      {/* 5. 2 Empirical Charts (40px radius, 1px Ash border) */}
      <div
        style={{
          width: '100%',
          maxWidth: '1280px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
          gap: '24px',
        }}
      >
        {/* Left Chart: Seasonal Cyclone Frequency vs Risk */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            boxShadow: 'none',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <LineChart size={18} color="#2b59d1" />
              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                  fontSize: '18px',
                  fontWeight: 400,
                  color: '#242424',
                  letterSpacing: '-0.02em',
                }}
              >
                Seasonal Cyclone Frequency vs Coastal Risk
              </span>
            </div>
            <span
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                color: '#797776',
                padding: '3px 10px',
                borderRadius: '9999px',
                textTransform: 'uppercase',
                letterSpacing: '-0.02em',
              }}
            >
              IMD 10-YR HISTORIC
            </span>
          </div>

          {/* Legend */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '24px', fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace', fontSize: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '16px', height: '2px', backgroundColor: '#f37a0a' }} />
              <span style={{ color: '#4e4d4d' }}>Cyclone Frequency</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '16px', height: '2px', backgroundColor: '#2b59d1' }} />
              <span style={{ color: '#242424', fontWeight: 500 }}>Varidhi Marine Risk Index</span>
            </div>
          </div>

          {/* SVG Line Chart */}
          <div style={{ width: '100%', height: '220px', position: 'relative' }}>
            <svg viewBox="0 0 500 220" style={{ width: '100%', height: '100%' }}>
              <line x1="35" y1="20" x2="490" y2="20" stroke="#cecac8" strokeWidth="0.8" strokeDasharray="3,3" />
              <line x1="35" y1="60" x2="490" y2="60" stroke="#cecac8" strokeWidth="0.8" strokeDasharray="3,3" />
              <line x1="35" y1="100" x2="490" y2="100" stroke="#cecac8" strokeWidth="0.8" strokeDasharray="3,3" />
              <line x1="35" y1="140" x2="490" y2="140" stroke="#cecac8" strokeWidth="0.8" strokeDasharray="3,3" />
              <line x1="35" y1="180" x2="490" y2="180" stroke="#cecac8" strokeWidth="1" />

              <text x="24" y="24" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">80</text>
              <text x="24" y="64" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">60</text>
              <text x="24" y="104" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">40</text>
              <text x="24" y="144" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">20</text>
              <text x="24" y="184" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">0</text>

              {/* Crimson / Coral Frequency Line */}
              <path
                d="M 45 174 L 85 175 L 125 174 L 165 172 L 205 168 L 245 172 L 285 173 L 325 170 L 365 168 L 405 169 L 445 172 L 485 174"
                fill="none"
                stroke="#f37a0a"
                strokeWidth="2"
              />

              {/* Lake Blue Risk Curve */}
              <path
                d="M 45 165 C 85 160, 125 145, 165 110 C 185 85, 205 60, 220 60 C 240 60, 260 85, 290 100 C 320 115, 340 100, 360 80 C 375 60, 395 55, 410 60 C 430 70, 460 120, 485 155"
                fill="none"
                stroke="#2b59d1"
                strokeWidth="2.2"
              />

              <circle cx="45" cy="165" r="3" fill="#2b59d1" />
              <circle cx="125" cy="145" r="3" fill="#2b59d1" />
              <circle cx="165" cy="110" r="3" fill="#2b59d1" />
              <circle cx="220" cy="60" r="3" fill="#2b59d1" />
              <circle cx="290" cy="100" r="3" fill="#2b59d1" />
              <circle cx="360" cy="80" r="3" fill="#2b59d1" />
              <circle cx="410" cy="60" r="3" fill="#2b59d1" />
              <circle cx="485" cy="155" r="3" fill="#2b59d1" />

              <text x="45" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">Jan</text>
              <text x="125" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">Mar</text>
              <text x="220" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">May</text>
              <text x="290" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">Jul</text>
              <text x="360" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">Sep</text>
              <text x="410" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">Oct</text>
              <text x="485" y="200" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)" textAnchor="middle">Dec</text>
            </svg>
          </div>
        </div>

        {/* Right Chart: Time to Advisory Broadcast */}
        <div
          className="monad-card"
          style={{
            backgroundColor: '#f6f3f1',
            border: '1px solid #cecac8',
            borderRadius: '40px',
            padding: '40px',
            boxShadow: 'none',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '8px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={18} color="#2b59d1" />
              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                  fontSize: '18px',
                  fontWeight: 400,
                  color: '#242424',
                  letterSpacing: '-0.02em',
                }}
              >
                Emergency Advisory Latency (Minutes)
              </span>
            </div>
            <span
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                backgroundColor: '#f6f3f1',
                border: '1px solid #cecac8',
                color: '#2b59d1',
                padding: '3px 10px',
                borderRadius: '9999px',
                fontWeight: 500,
                letterSpacing: '-0.02em',
              }}
            >
              98% REDUCTION
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '24px', fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace', fontSize: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#cecac8', borderRadius: '3px' }} />
              <span style={{ color: '#4e4d4d' }}>Manual Agency Assembly</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ width: '12px', height: '12px', backgroundColor: '#2b59d1', borderRadius: '3px' }} />
              <span style={{ color: '#242424', fontWeight: 500 }}>Varidhi Multi-Agent Swarm</span>
            </div>
          </div>

          {/* SVG Bar Comparison */}
          <div style={{ width: '100%', height: '220px', position: 'relative' }}>
            <svg viewBox="0 0 500 220" style={{ width: '100%', height: '100%' }}>
              <line x1="120" y1="20" x2="120" y2="185" stroke="#cecac8" strokeWidth="1" />

              {/* Row 1 */}
              <text x="110" y="55" fontSize="11" fill="#242424" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">Cyclone Alert</text>
              <rect x="120" y="40" width="310" height="18" rx="4" fill="#cecac8" />
              <text x="440" y="54" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)">65 min</text>
              <rect x="120" y="62" width="18" height="18" rx="4" fill="#2b59d1" />
              <text x="145" y="76" fontSize="10" fill="#2b59d1" fontWeight="500" fontFamily="var(--font-abc-diatype-mono)">1.2 min</text>

              {/* Row 2 */}
              <text x="110" y="115" fontSize="11" fill="#242424" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">PFZ Navigation</text>
              <rect x="120" y="100" width="220" height="18" rx="4" fill="#cecac8" />
              <text x="350" y="114" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)">45 min</text>
              <rect x="120" y="122" width="14" height="18" rx="4" fill="#2b59d1" />
              <text x="142" y="136" fontSize="10" fill="#2b59d1" fontWeight="500" fontFamily="var(--font-abc-diatype-mono)">0.8 min</text>

              {/* Row 3 */}
              <text x="110" y="172" fontSize="11" fill="#242424" fontFamily="var(--font-abc-diatype-mono)" textAnchor="end">Vessel Evac</text>
              <rect x="120" y="157" width="360" height="18" rx="4" fill="#cecac8" />
              <text x="488" y="171" fontSize="10" fill="#797776" fontFamily="var(--font-abc-diatype-mono)">90 min</text>
              <rect x="120" y="179" width="24" height="18" rx="4" fill="#2b59d1" />
              <text x="152" y="193" fontSize="10" fill="#2b59d1" fontWeight="500" fontFamily="var(--font-abc-diatype-mono)">2.0 min</text>
            </svg>
          </div>
        </div>
      </div>
    </section>
  );
};
