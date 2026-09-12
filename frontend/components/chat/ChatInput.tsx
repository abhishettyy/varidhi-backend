'use client';

import React, { useState } from 'react';
import { ArrowRight, Mic, Sparkles } from 'lucide-react';

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

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 8px 6px 16px',
        backgroundColor: '#ffffff',
        border: `1px solid ${isFocused ? '#2b59d1' : '#cecac8'}`,
        borderRadius: '100px',
        boxShadow: isFocused ? '0 0 0 1px #2b59d1' : 'none',
        transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ color: '#767371', display: 'flex', alignItems: 'center' }}>
        <Sparkles size={15} />
      </div>

      <input
        type="text"
        value={input}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onChange={(e) => setInput(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        style={{
          flex: 1,
          backgroundColor: 'transparent',
          border: 'none',
          outline: 'none',
          color: '#242424',
          fontSize: '13px',
          fontFamily: 'inherit',
        }}
      />

      <button
        type="button"
        title="Voice Prompt"
        onClick={() => {
          setInput('Where should I fish tomorrow morning?');
        }}
        style={{
          background: 'none',
          border: 'none',
          color: '#767371',
          cursor: 'pointer',
          padding: '6px',
          borderRadius: '9999px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'color 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = '#242424')}
        onMouseLeave={(e) => (e.currentTarget.style.color = '#767371')}
      >
        <Mic size={15} />
      </button>

      <button
        type="submit"
        disabled={!input.trim() || disabled}
        style={{
          backgroundColor: input.trim() && !disabled ? '#2b59d1' : '#cecac8',
          border: 'none',
          color: '#f6f3f1',
          cursor: input.trim() && !disabled ? 'pointer' : 'not-allowed',
          padding: '8px 18px',
          borderRadius: '100px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          fontWeight: 500,
          fontFamily: 'inherit',
          transition: 'background-color 0.15s ease',
        }}
      >
        <span>QUERY</span>
        <ArrowRight size={13} />
      </button>
    </form>
  );
};
