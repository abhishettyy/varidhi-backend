'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChatMessageItem, QuickPrompt } from '@/types/chat';
import { RoleType } from '@/types/marine';
import { queryVaridhiAI } from '@/services/api/chatApi';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { QuickPrompts } from './QuickPrompts';
import { Sparkles, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';

interface ChatPanelProps {
  role: RoleType;
  quickPrompts: QuickPrompt[];
  title?: string;
  subtitle?: string;
  defaultExpanded?: boolean;
  onFocusZone?: (zoneId: string) => void;
  onViewLayer?: (layerKey: string) => void;
  initialMessage?: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  role,
  quickPrompts,
  title = 'Ask Varidhi Intelligence',
  subtitle = 'Natural-language marine advisory & validation',
  defaultExpanded = true,
  onFocusZone,
  onViewLayer,
  initialMessage,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessageItem[]>(() => {
    const welcome =
      role === 'fisherman'
        ? 'Welcome to Varidhi Fisherman Advisory. Ask where to fish tomorrow, check sea conditions, or verify safe fishing zones near Mangalore.'
        : role === 'maritime_operator' || role === 'general'
        ? 'Varidhi Marine Operations Assistant ready. Ask for regional risk assessments, restricted sanctuary activity, or weather warnings.'
        : 'Varidhi Oceanographic Research Assistant ready. Query PFZ SST front convergence, chlorophyll anomalies, or 7-day trends.';

    return [
      {
        id: 'msg_welcome',
        sender: 'assistant',
        timestamp: 'Just now',
        content: initialMessage || welcome,
      },
    ];
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessageItem = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await queryVaridhiAI(text, role);

      const aiMsg: ChatMessageItem = {
        id: response.response_id,
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: response.markdown_content,
        data: response,
      };

      setMessages((prev) => [...prev, aiMsg]);

      if (response.visual_payload?.focus_zone_id && onFocusZone) {
        onFocusZone(response.visual_payload.focus_zone_id);
      }
      if (response.visual_payload?.highlight_layer && onViewLayer) {
        onViewLayer(response.visual_payload.highlight_layer);
      }
    } catch (err) {
      const errorMsg: ChatMessageItem = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        timestamp: 'Error',
        content: 'Unable to complete advisory query at this time. Please try again.',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f6f3f1',
        border: '1px solid #cecac8',
        borderRadius: '24px',
        overflow: 'hidden',
        width: '100%',
        maxHeight: isExpanded ? '560px' : '52px',
        transition: 'max-height 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Header / Collapse Bar */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          padding: '14px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          backgroundColor: '#f6f3f1',
          borderBottom: isExpanded ? '1px solid #cecac8' : 'none',
          userSelect: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: '9999px',
              backgroundColor: '#cfdaf5',
              border: '1px solid #cecac8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#2b59d1',
            }}
          >
            <Sparkles size={14} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span
                style={{
                  fontFamily: 'var(--font-untitled-serif), serif',
                  fontSize: '17px',
                  fontWeight: 400,
                  letterSpacing: '-0.02em',
                  color: '#242424',
                }}
              >
                {title}
              </span>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '2px 8px',
                  borderRadius: '9999px',
                  border: '1px solid #cecac8',
                  fontSize: '10px',
                  color: '#767371',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                <span style={{ width: 5, height: 5, borderRadius: '50%', backgroundColor: '#2b59d1' }} />
                Online
              </span>
            </div>
            <span style={{ fontSize: '11px', color: '#767371', marginTop: '2px', display: 'block' }}>
              {subtitle}
            </span>
          </div>
        </div>

        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: '9999px',
            border: '1px solid #cecac8',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#767371',
            backgroundColor: '#ffffff',
          }}
        >
          {isExpanded ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </div>
      </div>

      {/* Expanded Body */}
      {isExpanded && (
        <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0, padding: '16px' }}>
          {/* Quick Prompts Bar */}
          <div style={{ marginBottom: '12px' }}>
            <QuickPrompts
              prompts={quickPrompts}
              onSelectPrompt={(p) => handleSendMessage(p.query)}
              disabled={isLoading}
            />
          </div>

          {/* Messages Scroll Area */}
          <div
            ref={scrollRef}
            className="chat-scroll-area"
            style={{
              flex: 1,
              minHeight: '160px',
              maxHeight: '340px',
              paddingRight: '6px',
              marginBottom: '14px',
              overflowY: 'auto',
            }}
          >
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                onFocusZone={onFocusZone}
                onViewLayer={onViewLayer}
              />
            ))}

            {isLoading && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: '#2b59d1',
                  fontSize: '12px',
                  padding: '10px 14px',
                  borderRadius: '16px',
                  backgroundColor: '#cfdaf5',
                  border: '1px solid #cecac8',
                  width: 'fit-content',
                }}
              >
                <Loader2 size={14} className="animate-spin" />
                <span>Interrogating oceanographic models & safety rules...</span>
              </div>
            )}
          </div>

          {/* Input Box */}
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading}
            placeholder={
              role === 'fisherman'
                ? 'Ask: "Where should I fish tomorrow?" or "Is it safe?"'
                : role === 'maritime_operator'
                ? 'Ask: "Show high-risk areas" or "Vessels near sanctuary"'
                : 'Ask: "Why is PFZ strength high?" or "Compare Zone A & B"'
            }
          />
        </div>
      )}
    </div>
  );
};
