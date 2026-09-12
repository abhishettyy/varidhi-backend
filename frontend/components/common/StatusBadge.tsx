'use client';

import React from 'react';
import { SafetySeverity, RecommendationStatus, LegalStatus } from '@/types/marine';
import { ShieldCheck, AlertTriangle, AlertOctagon, CheckCircle2, Lock } from 'lucide-react';

interface StatusBadgeProps {
  type: 'safety' | 'recommendation' | 'legal';
  value: SafetySeverity | RecommendationStatus | LegalStatus | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  type,
  value,
  size = 'md',
  showIcon = true,
}) => {
  let label = String(value).toUpperCase();
  let bg = '#f6f3f1';
  let color = '#242424';
  let Icon = ShieldCheck;

  if (type === 'safety') {
    switch (value) {
      case 'safe_green':
        label = 'SAFE';
        bg = '#cfdaf5'; // Periwinkle Mist
        color = '#2b59d1';
        Icon = ShieldCheck;
        break;
      case 'caution_yellow':
        label = 'CAUTION';
        bg = 'rgba(236, 218, 152, 0.35)'; // Gold
        color = '#242424';
        Icon = AlertTriangle;
        break;
      case 'warning_orange':
        label = 'WARNING';
        bg = 'rgba(243, 122, 10, 0.25)'; // Crimson
        color = '#242424';
        Icon = AlertTriangle;
        break;
      case 'danger_red':
        label = 'DANGER';
        bg = 'rgba(255, 148, 115, 0.35)'; // Coral
        color = '#242424';
        Icon = AlertOctagon;
        break;
    }
  } else if (type === 'recommendation') {
    switch (value) {
      case 'recommended':
        label = 'RECOMMENDED';
        bg = '#cfdaf5';
        color = '#2b59d1';
        Icon = CheckCircle2;
        break;
      case 'high_risk':
        label = 'HIGH RISK';
        bg = 'rgba(255, 148, 115, 0.35)';
        color = '#242424';
        Icon = AlertOctagon;
        break;
      case 'restricted':
        label = 'RESTRICTED';
        bg = '#f6f3f1';
        color = '#797776';
        Icon = Lock;
        break;
      default:
        label = 'ALTERNATIVE';
        bg = 'rgba(236, 218, 152, 0.35)';
        color = '#242424';
        Icon = AlertTriangle;
    }
  } else if (type === 'legal') {
    if (value === 'allowed') {
      label = 'ALLOWED';
      bg = '#cfdaf5';
      color = '#2b59d1';
      Icon = CheckCircle2;
    } else {
      label = 'RESTRICTED';
      bg = '#f6f3f1';
      color = '#797776';
      Icon = Lock;
    }
  }

  const padding = size === 'sm' ? '2px 8px' : size === 'lg' ? '6px 14px' : '4px 10px';
  const fontSize = size === 'sm' ? '11px' : size === 'lg' ? '13px' : '12px';
  const iconSize = size === 'sm' ? 12 : size === 'lg' ? 14 : 13;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '5px',
        padding,
        borderRadius: '9999px',
        backgroundColor: bg,
        border: '1px solid #cecac8',
        color,
        fontSize,
        fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
        fontWeight: 500,
        letterSpacing: '-0.02em',
        lineHeight: 1,
        textTransform: 'uppercase',
      }}
    >
      {showIcon && <Icon size={iconSize} />}
      <span>{label}</span>
    </span>
  );
};
