'use client';

import React from 'react';
import { 
  Satellite, 
  Waves, 
  Wind, 
  Ship, 
  ShieldCheck, 
  Cpu, 
  Compass, 
  FileText,
  Radio
} from 'lucide-react';

export const ArchitectureSection: React.FC = () => {
  const sourceNodes = [
    { name: 'ISRO MOSDAC SST', icon: Satellite },
    { name: 'INCOIS PFZ / WAVE', icon: Waves },
    { name: 'IMD CYCLONE VECTORS', icon: Wind },
    { name: 'COASTAL AIS RADAR', icon: Ship },
    { name: 'EEZ BOUNDARY REEFS', icon: ShieldCheck },
  ];

  const destinationNodes = [
    { name: 'FISHERMAN ADVISORY', icon: Compass },
    { name: 'MARITIME COMMAND HUD', icon: Radio },
    { name: 'RESEARCHER GIS DOSSIER', icon: FileText },
  ];

  return (
    <section
      id="architecture"
      style={{
        width: '100%',
        backgroundColor: '#f6f3f1',
        borderTop: '1px solid #cecac8',
        borderBottom: '1px solid #cecac8',
        padding: '80px 24px 104px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden',
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
              backgroundColor: '#a7fccd',
            }}
          />
          DATA PIPELINE ARCHITECTURE
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
        Autonomous Swarm Pipeline & Orchestration
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
        Built on LangGraph state channels. Independent domain agents ingest heterogeneous telemetry streams, compute deterministic physical bounds, and route verifiable evidence to downstream operational sinks.
      </p>

      {/* 4. Monad Pipeline Diagram Container */}
      <div
        style={{
          width: '100%',
          maxWidth: '1200px',
          backgroundColor: '#f6f3f1',
          border: '1px solid #cecac8',
          borderRadius: '40px',
          padding: '48px 32px',
          position: 'relative',
        }}
      >
        {/* Soft Mint radial glow at center hub suggesting data normalization */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '380px',
            height: '380px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(167, 252, 205, 0.45) 0%, rgba(160, 181, 235, 0.25) 50%, transparent 75%)',
            filter: 'blur(50px)',
            pointerEvents: 'none',
            zIndex: 0,
          }}
        />

        <div
          style={{
            position: 'relative',
            zIndex: 1,
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '32px',
            alignItems: 'center',
          }}
        >
          {/* Column 1: Sources */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                color: '#797776',
                textTransform: 'uppercase',
                letterSpacing: '-0.02em',
                marginBottom: '4px',
              }}
            >
              INGESTION NODES [5 STREAM FEEDS]
            </div>

            {sourceNodes.map((src, idx) => {
              const Icon = src.icon;
              return (
                <div
                  key={idx}
                  className="monad-node-tag"
                  style={{
                    backgroundColor: '#f6f3f1',
                    border: '1px solid #cecac8',
                    borderRadius: '9999px',
                    padding: '12px 20px',
                    fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                    fontSize: '13px',
                    textTransform: 'uppercase',
                    letterSpacing: '-0.02em',
                    color: '#242424',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    boxShadow: 'none',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Icon size={15} color="#242424" />
                    <span>{src.name}</span>
                  </div>
                  <span style={{ color: '#cecac8', fontSize: '11px' }}>0{idx + 1}</span>
                </div>
              );
            })}
          </div>

          {/* Column 2: Normalization Hub (Center) */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              padding: '24px',
            }}
          >
            {/* Center Core Node */}
            <div
              style={{
                width: '110px',
                height: '110px',
                borderRadius: '50%',
                backgroundColor: '#f6f3f1',
                border: '1px solid #242424',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                marginBottom: '16px',
                boxShadow: '0 0 20px rgba(167, 252, 205, 0.4)',
              }}
            >
              <Cpu size={28} color="#242424" />
              <span
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '10px',
                  fontWeight: 500,
                  textTransform: 'uppercase',
                  letterSpacing: '-0.02em',
                  color: '#242424',
                }}
              >
                ORCA CORE
              </span>
            </div>

            <div
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '22px',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
                marginBottom: '8px',
              }}
            >
              Deterministic Synthesis Hub
            </div>

            <p
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '13px',
                color: '#4e4d4d',
                lineHeight: 1.45,
                maxWidth: '280px',
                letterSpacing: '-0.02em',
              }}
            >
              Physics verification & spatial intersection math computed prior to LLM reasoning.
            </p>
          </div>

          {/* Column 3: Destination Sinks */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div
              style={{
                fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                fontSize: '11px',
                color: '#797776',
                textTransform: 'uppercase',
                letterSpacing: '-0.02em',
                marginBottom: '4px',
              }}
            >
              DESTINATIONS & SINKS
            </div>

            {destinationNodes.map((dst, idx) => {
              const Icon = dst.icon;
              return (
                <div
                  key={idx}
                  className="monad-node-tag"
                  style={{
                    backgroundColor: idx === 1 ? '#cfdaf5' : '#f6f3f1',
                    border: '1px solid #cecac8',
                    borderRadius: '9999px',
                    padding: '14px 22px',
                    fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                    fontSize: '13px',
                    textTransform: 'uppercase',
                    letterSpacing: '-0.02em',
                    color: '#242424',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                  }}
                >
                  <Icon size={16} color={idx === 1 ? '#2b59d1' : '#242424'} />
                  <span>{dst.name}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
