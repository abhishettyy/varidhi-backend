'use client';

import React from 'react';
import { RecommendationStatus, LegalStatus } from '@/types/marine';
import { ShieldCheck, AlertTriangle, CheckCircle2, Lock } from 'lucide-react';

interface BadgeProps {
  status: RecommendationStatus | LegalStatus;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({ status, size = 'md', showIcon = true }) => {
  const getBadgeConfig = () => {
    switch (status) {
      case 'recommended':
        return {
          label: 'RECOMMENDED',
          bg: '#cfdaf5', // Periwinkle Mist
          color: '#2b59d1', // Lake Blue
          icon: ShieldCheck,
        };
      case 'alternative':
        return {
          label: 'ALTERNATIVE',
          bg: 'rgba(236, 218, 152, 0.25)', // Gold
          color: '#242424',
          icon: CheckCircle2,
        };
      case 'high_risk':
        return {
          label: 'HIGH RISK',
          bg: 'rgba(255, 148, 115, 0.25)', // Coral
          color: '#242424',
          icon: AlertTriangle,
        };
      case 'restricted':
        return {
          label: 'RESTRICTED',
          bg: '#f6f3f1',
          color: '#797776',
          icon: Lock,
        };
      case 'allowed':
        return {
          label: 'LEGAL: ALLOWED',
          bg: '#cfdaf5',
          color: '#2b59d1',
          icon: CheckCircle2,
        };
      default:
        return {
          label: String(status).toUpperCase(),
          bg: '#f6f3f1',
          color: '#4e4d4d',
          icon: AlertTriangle,
        };
    }
  };

  const config = getBadgeConfig();
  const IconComponent = config.icon;

  const sizeStyles = {
    sm: { padding: '2px 8px', fontSize: '11px', gap: '4px', iconSize: 12 },
    md: { padding: '4px 10px', fontSize: '12px', gap: '5px', iconSize: 13 },
    lg: { padding: '6px 14px', fontSize: '13px', gap: '6px', iconSize: 14 },
  }[size];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: sizeStyles.gap,
        padding: sizeStyles.padding,
        fontSize: sizeStyles.fontSize,
        fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
        fontWeight: 500,
        borderRadius: '9999px',
        backgroundColor: config.bg,
        border: '1px solid #cecac8',
        color: config.color,
        letterSpacing: '-0.02em',
        textTransform: 'uppercase',
      }}
    >
      {showIcon && <IconComponent size={sizeStyles.iconSize} />}
      <span>{config.label}</span>
    </span>
  );
};
