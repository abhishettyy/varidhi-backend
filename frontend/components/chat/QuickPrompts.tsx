'use client';

import React from 'react';
import { QuickPrompt } from '@/types/chat';

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
        alignItems: 'center',
        gap: '8px',
        overflowX: 'auto',
        padding: '2px 0',
        scrollbarWidth: 'none',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <span
        style={{
          fontSize: '10px',
          color: '#767371',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          flexShrink: 0,
        }}
      >
        PROMPTS:
      </span>
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
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
            color: '#242424',
            fontSize: '11px',
            fontFamily: 'inherit',
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all 0.15s ease',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            if (!disabled) {
              e.currentTarget.style.backgroundColor = '#cfdaf5';
              e.currentTarget.style.borderColor = '#2b59d1';
            }
          }}
          onMouseLeave={(e) => {
            if (!disabled) {
              e.currentTarget.style.backgroundColor = '#ffffff';
              e.currentTarget.style.borderColor = '#cecac8';
            }
          }}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
};
