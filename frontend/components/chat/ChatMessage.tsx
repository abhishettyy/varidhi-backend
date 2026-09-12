'use client';

import React from 'react';
import { ChatMessageItem } from '@/types/chat';
import { AIResponseCard } from './AIResponseCard';
import { MarkdownRenderer } from './MarkdownRenderer';
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
      className={isUser ? 'chat-msg-user' : 'chat-msg-ai'}
      style={{
        display: 'flex',
        gap: '10px',
        alignItems: 'flex-start',
        marginBottom: '14px',
        flexDirection: isUser ? 'row-reverse' : 'row',
        fontFamily: 'var(--font-sans)',
      }}
    >
      {/* Sender Avatar */}
      <div
        style={{
          width: 28,
          height: 28,
          borderRadius: '9999px',
          backgroundColor: isUser ? '#242424' : '#cfdaf5',
          border: '1px solid #cecac8',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: isUser ? '#f6f3f1' : '#2b59d1',
          flexShrink: 0,
          marginTop: '2px',
        }}
      >
        {isUser ? <User size={13} /> : <Sparkles size={13} />}
      </div>

      {/* Message Bubble */}
      <div
        style={{
          maxWidth: '88%',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          alignItems: isUser ? 'flex-end' : 'flex-start',
        }}
      >
        {/* Timestamp */}
        <span
          style={{
            fontSize: '9px',
            color: '#a8a29e',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            paddingInline: '4px',
          }}
        >
          {isUser ? 'You' : 'Varidhi Intelligence'} · {message.timestamp}
        </span>

        {/* Bubble */}
        <div
          style={{
            padding: isUser ? '10px 16px' : '14px 18px',
            borderRadius: isUser ? '18px 18px 6px 18px' : '6px 18px 18px 18px',
            backgroundColor: isUser ? '#242424' : '#ffffff',
            border: isUser ? 'none' : '1px solid #cecac8',
            color: isUser ? '#f6f3f1' : '#242424',
            boxShadow: isUser ? 'none' : '0 1px 4px rgba(36,36,36,0.04)',
          }}
        >
          {isUser || !message.data ? (
            isUser ? (
              <p
                style={{
                  fontSize: '13px',
                  lineHeight: 1.6,
                  margin: 0,
                  color: '#f6f3f1',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'var(--font-sans)',
                }}
              >
                {message.content}
              </p>
            ) : (
              // AI message without structured data — render as markdown
              <MarkdownRenderer content={message.content} />
            )
          ) : (
            <AIResponseCard
              data={message.data}
              onFocusZone={onFocusZone}
              onViewLayer={onViewLayer}
            />
          )}
        </div>
      </div>
    </div>
  );
};
