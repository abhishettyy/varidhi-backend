'use client';

import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  position?: 'left' | 'right' | 'bottom';
  width?: string | number;
  children: React.ReactNode;
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  position = 'right',
  width = 440,
  children,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isBottom = position === 'bottom';

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        display: 'flex',
        justifyContent: position === 'right' ? 'flex-end' : position === 'left' ? 'flex-start' : 'center',
        alignItems: isBottom ? 'flex-end' : 'stretch',
        backgroundColor: 'rgba(36, 36, 36, 0.4)',
        backdropFilter: 'blur(4px)',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          width: isBottom ? '100%' : width,
          maxHeight: isBottom ? '85vh' : '100vh',
          height: isBottom ? 'auto' : '100vh',
          backgroundColor: '#f6f3f1',
          borderLeft: position === 'right' ? '1px solid #cecac8' : 'none',
          borderRight: position === 'left' ? '1px solid #cecac8' : 'none',
          borderTop: isBottom ? '1px solid #cecac8' : 'none',
          borderTopLeftRadius: isBottom ? '40px' : 0,
          borderTopRightRadius: isBottom ? '40px' : 0,
          boxShadow: 'none',
          display: 'flex',
          flexDirection: 'column',
          fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '24px 28px',
            borderBottom: '1px solid #cecac8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#f6f3f1',
          }}
        >
          <div>
            <h3
              style={{
                fontFamily: 'var(--font-untitled-serif), Georgia, serif',
                fontSize: '1.25rem',
                fontWeight: 400,
                color: '#242424',
                letterSpacing: '-0.02em',
                margin: 0,
              }}
            >
              {title}
            </h3>
            {subtitle && (
              <p
                style={{
                  fontFamily: 'var(--font-abc-diatype-mono), ui-monospace, monospace',
                  fontSize: '11px',
                  color: '#797776',
                  marginTop: '4px',
                  letterSpacing: '-0.02em',
                  textTransform: 'uppercase',
                }}
              >
                {subtitle}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            aria-label="Close panel"
            style={{
              background: 'transparent',
              border: '1px solid #cecac8',
              color: '#242424',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background-color 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(36, 36, 36, 0.06)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '28px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {children}
        </div>
      </div>
    </div>
  );
};
