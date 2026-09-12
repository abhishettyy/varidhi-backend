'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { AUTHORITY_QUICK_PROMPTS } from '@/services/api/chatApi';

export default function AuthorityChatPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f6f3f1',
        color: '#242424',
        padding: '36px 20px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      <div style={{ maxWidth: '780px', width: '100%' }}>
        <div style={{ marginBottom: '20px' }}>
          <Link
            href="/authority"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              color: '#242424',
              backgroundColor: '#ffffff',
              border: '1px solid #cecac8',
              padding: '7px 16px',
              borderRadius: '100px',
              textDecoration: 'none',
              fontSize: '11px',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              transition: 'background-color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
          >
            <ArrowLeft size={13} />
            <span>RETURN TO WORKSPACE</span>
          </Link>
        </div>

        <ChatPanel
          role="maritime_operator"
          quickPrompts={AUTHORITY_QUICK_PROMPTS}
          title="Varidhi Maritime Surveillance Intelligence"
          subtitle="Full-screen dedicated operational risk & enforcement chat"
          defaultExpanded={true}
        />
      </div>
    </div>
  );
}
