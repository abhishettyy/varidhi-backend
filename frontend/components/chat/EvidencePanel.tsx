'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2, Microscope } from 'lucide-react';

interface EvidencePanelProps {
  evidenceList: string[];
  title?: string;
  defaultExpanded?: boolean;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  evidenceList,
  title = 'Supporting Scientific Evidence',
  defaultExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!evidenceList || evidenceList.length === 0) return null;

  return (
    <div
      style={{
        marginTop: '10px',
        borderRadius: '16px',
        backgroundColor: '#f6f3f1',
        border: '1px solid #cecac8',
        overflow: 'hidden',
        fontSize: '12px',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: '100%',
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'transparent',
          border: 'none',
          color: '#242424',
          cursor: 'pointer',
          fontWeight: 500,
          textAlign: 'left',
          fontFamily: 'inherit',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Microscope size={14} color="#2b59d1" />
          <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {title}
          </span>
          <span style={{ fontSize: '10px', color: '#767371' }}>({evidenceList.length} points)</span>
        </div>
        <div
          style={{
            width: 22,
            height: 22,
            borderRadius: '9999px',
            border: '1px solid #cecac8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#ffffff',
            color: '#767371',
          }}
        >
          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </div>
      </button>

      {isExpanded && (
        <div
          style={{
            padding: '12px 14px',
            borderTop: '1px solid #cecac8',
            backgroundColor: '#ffffff',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          {evidenceList.map((item, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', color: '#242424' }}>
              <div style={{ color: '#2b59d1', marginTop: '2px', flexShrink: 0 }}>
                <CheckCircle2 size={13} />
              </div>
              <span style={{ lineHeight: 1.5, fontSize: '12px' }}>{item}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
