'use client';

import React, { useState } from 'react';
import { ArrowRight, Mic } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  placeholder = 'Query marine intelligence models or ask for advice...',
  disabled = false,
}) => {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const canSend = input.trim() && !disabled;

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '7px 8px 7px 16px',
        backgroundColor: disabled ? '#f6f3f1' : '#ffffff',
        border: `1px solid ${isFocused ? '#2b59d1' : '#cecac8'}`,
        borderRadius: '100px',
        boxShadow: isFocused ? '0 0 0 3px rgba(43, 89, 209, 0.1)' : 'none',
        transition: 'border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
        opacity: disabled ? 0.7 : 1,
      }}
    >
      {/* Varidhi pulse dot when idle, wave when loading */}
      <div
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          backgroundColor: disabled ? '#2b59d1' : '#cecac8',
          flexShrink: 0,
          animation: disabled ? 'varPulse 1s ease-in-out infinite' : 'none',
          transition: 'background-color 0.2s ease',
        }}
      />

      <input
        type="text"
        value={input}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onChange={(e) => setInput(e.target.value)}
        placeholder={disabled ? 'Processing query...' : placeholder}
        disabled={disabled}
        style={{
          flex: 1,
          backgroundColor: 'transparent',
          border: 'none',
          outline: 'none',
          color: '#242424',
          fontSize: '12px',
          fontFamily: 'inherit',
          letterSpacing: '-0.01em',
        }}
      />

      {/* Mic shortcut button */}
      <button
        type="button"
        title="Sample query"
        onClick={() => {
          if (!disabled) setInput('Where should I fish tomorrow morning?');
        }}
        disabled={disabled}
        style={{
          background: 'none',
          border: 'none',
          color: '#cecac8',
          cursor: disabled ? 'not-allowed' : 'pointer',
          padding: '5px',
          borderRadius: '9999px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'color 0.15s ease',
        }}
        onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.color = '#767371'; }}
        onMouseLeave={(e) => { e.currentTarget.style.color = '#cecac8'; }}
      >
        <Mic size={14} />
      </button>

      {/* Send button */}
      <button
        type="submit"
        disabled={!canSend}
        style={{
          backgroundColor: canSend ? '#2b59d1' : '#e8e5e3',
          border: 'none',
          color: canSend ? '#ffffff' : '#a8a29e',
          cursor: canSend ? 'pointer' : 'not-allowed',
          padding: '8px 16px',
          borderRadius: '100px',
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          fontSize: '11px',
          fontWeight: 600,
          fontFamily: 'inherit',
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          transition: 'background-color 0.15s ease, color 0.15s ease, transform 0.1s ease',
          flexShrink: 0,
        }}
        onMouseEnter={(e) => { if (canSend) e.currentTarget.style.transform = 'scale(1.03)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
      >
        <span>Query</span>
        <ArrowRight size={12} />
      </button>
    </form>
  );
};
