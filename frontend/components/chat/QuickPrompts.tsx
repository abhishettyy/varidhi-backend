'use client';

import React from 'react';
import { QuickPrompt } from '@/types/chat';
import { Zap } from 'lucide-react';

const CATEGORY_ICONS: Record<string, string> = {
  advisory: '⚓',
  safety: '🛡',
  monitoring: '📡',
  analytics: '📊',
};

interface QuickPromptsProps {
  prompts: QuickPrompt[];
  onSelectPrompt: (prompt: QuickPrompt) => void;
  disabled?: boolean;
}

export const QuickPrompts: React.FC<QuickPromptsProps> = ({
  prompts,
  onSelectPrompt,
  disabled = false,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Label */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <Zap size={10} style={{ color: '#2b59d1' }} />
        <span
          style={{
            fontSize: '9px',
            color: '#a8a29e',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            fontWeight: 600,
          }}
        >
          Quick queries
        </span>
      </div>

      {/* Chip row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          overflowX: 'auto',
          padding: '2px 0 4px 0',
          scrollbarWidth: 'none',
        }}
      >
        {prompts.map((p) => (
          <button
            key={p.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(p)}
            style={{
              whiteSpace: 'nowrap',
              padding: '5px 12px',
              borderRadius: '9999px',
              backgroundColor: disabled ? '#f6f3f1' : '#ffffff',
              border: '1px solid #e0dedc',
              color: disabled ? '#a8a29e' : '#242424',
              fontSize: '11px',
              fontFamily: 'inherit',
              cursor: disabled ? 'not-allowed' : 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              transition: 'all 0.15s ease',
              flexShrink: 0,
              letterSpacing: '-0.01em',
            }}
            onMouseEnter={(e) => {
              if (!disabled) {
                e.currentTarget.style.backgroundColor = '#cfdaf5';
                e.currentTarget.style.borderColor = '#a0b5eb';
                e.currentTarget.style.color = '#2b59d1';
              }
            }}
            onMouseLeave={(e) => {
              if (!disabled) {
                e.currentTarget.style.backgroundColor = '#ffffff';
                e.currentTarget.style.borderColor = '#e0dedc';
                e.currentTarget.style.color = '#242424';
              }
            }}
          >
            {p.category && (
              <span style={{ fontSize: '10px', lineHeight: 1 }}>
                {CATEGORY_ICONS[p.category] || '↗'}
              </span>
            )}
            {p.label}
          </button>
        ))}
      </div>
    </div>
  );
};
