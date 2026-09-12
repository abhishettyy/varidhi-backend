'use client';

import React from 'react';
import { ChatMessageItem } from '@/types/chat';
import { AIResponseCard } from './AIResponseCard';
import { User, Sparkles } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageItem;
  onFocusZone?: (zoneId: string) => void;
  onViewLayer?: (layerKey: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onFocusZone,
  onViewLayer,
}) => {
  const isUser = message.sender === 'user';

  return (
    <div
      style={{
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-start',
        marginBottom: '16px',
        flexDirection: isUser ? 'row-reverse' : 'row',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Sender Avatar */}
      <div
        style={{
          width: 30,
          height: 30,
          borderRadius: '9999px',
          backgroundColor: isUser ? '#242424' : '#cfdaf5',
          border: '1px solid #cecac8',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: isUser ? '#f6f3f1' : '#2b59d1',
          flexShrink: 0,
        }}
      >
        {isUser ? <User size={14} /> : <Sparkles size={14} />}
      </div>

      {/* Message Bubble */}
      <div
        style={{
          maxWidth: '85%',
          padding: '14px 18px',
          borderRadius: '20px',
          backgroundColor: isUser ? '#ffffff' : '#f6f3f1',
          border: '1px solid #cecac8',
          color: '#242424',
        }}
      >
        {/* Timestamp & Sender */}
        <div
          style={{
            fontSize: '10px',
            color: '#767371',
            marginBottom: '8px',
            textAlign: isUser ? 'right' : 'left',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
          }}
        >
          {isUser ? 'OPERATOR' : 'VARIDHI SWARM'} • {message.timestamp}
        </div>

        {/* User plain text vs AI structured card */}
        {isUser || !message.data ? (
          <p
            style={{
              fontSize: '13px',
              lineHeight: 1.6,
              margin: 0,
              color: '#242424',
              whiteSpace: 'pre-wrap',
            }}
          >
            {message.content}
          </p>
        ) : (
          <AIResponseCard
            data={message.data}
            onFocusZone={onFocusZone}
            onViewLayer={onViewLayer}
          />
        )}
      </div>
    </div>
  );
};
