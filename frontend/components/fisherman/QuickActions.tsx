'use client';

import React from 'react';
import { Compass, Waves, ShieldCheck, Fish } from 'lucide-react';

interface QuickActionsProps {
  onTriggerAction: (query: string) => void;
  disabled?: boolean;
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  onTriggerAction,
  disabled = false,
}) => {
  const actions = [
    { label: 'Recommended Zone', query: 'Where should I fish tomorrow morning?', icon: Fish, color: '#2b59d1' },
    { label: 'Sea Conditions', query: 'What are the current sea conditions?', icon: Waves, color: '#2b59d1' },
    { label: 'Safety Check', query: 'Is it safe to go tomorrow?', icon: ShieldCheck, color: '#2b59d1' },
    { label: 'Nearest PFZ', query: 'Show nearest fishing zone.', icon: Compass, color: '#2b59d1' },
  ];

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {actions.map((act, idx) => {
        const Icon = act.icon;
        return (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onTriggerAction(act.query)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '9999px',
              backgroundColor: '#ffffff',
              border: '1px solid #cecac8',
              color: '#242424',
              fontSize: '11px',
              fontWeight: 500,
              fontFamily: 'inherit',
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.15s ease, border-color 0.15s ease',
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
            <Icon size={13} color={act.color} />
            <span>{act.label}</span>
          </button>
        );
      })}
    </div>
  );
};
