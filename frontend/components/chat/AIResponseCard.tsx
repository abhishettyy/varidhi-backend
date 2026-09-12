'use client';

import React from 'react';
import { AgentResponseData } from '@/types/chat';
import { StatusBadge } from '@/components/common/StatusBadge';
import { EvidencePanel } from './EvidencePanel';
import { Compass, ArrowRight } from 'lucide-react';

interface AIResponseCardProps {
  data: AgentResponseData;
  onFocusZone?: (zoneId: string) => void;
  onViewLayer?: (layerKey: string) => void;
}

export const AIResponseCard: React.FC<AIResponseCardProps> = ({
  data,
  onFocusZone,
  onViewLayer,
}) => {
  const { safety_alert, key_recommendations, evidence_summary, visual_payload, markdown_content } = data;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        width: '100%',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* 1. Safety Alert Banner if present */}
      {safety_alert && (
        <div
          style={{
            padding: '12px 16px',
            borderRadius: '16px',
            backgroundColor: 'rgba(255, 148, 115, 0.12)',
            border: '1px solid #ff9473',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
          }}
        >
          <div style={{ marginTop: '2px' }}>
            <StatusBadge type="safety" value={safety_alert.severity} size="sm" />
          </div>
          <div>
            <h4
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: '#242424',
                marginBottom: '4px',
                letterSpacing: '-0.01em',
              }}
            >
              {safety_alert.title}
            </h4>
            <p style={{ fontSize: '12px', color: '#767371', lineHeight: 1.5, margin: 0 }}>
              {safety_alert.description}
            </p>
            {safety_alert.action_advice && (
              <p
                style={{
                  fontSize: '11px',
                  color: '#2b59d1',
                  fontWeight: 500,
                  marginTop: '6px',
                  marginBottom: 0,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                ▸ Direct Action: {safety_alert.action_advice}
              </p>
            )}
          </div>
        </div>
      )}

      {/* 2. Markdown Content Text */}
      <div
        style={{
          fontSize: '13px',
          color: '#242424',
          lineHeight: 1.65,
          whiteSpace: 'pre-line',
        }}
      >
        {markdown_content}
      </div>

      {/* 3. Metric Badges Row */}
      {visual_payload?.metric_badges && (
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            marginTop: '2px',
          }}
        >
          {Object.entries(visual_payload.metric_badges).map(([key, val]) => (
            <div
              key={key}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '9999px',
                backgroundColor: '#ffffff',
                border: '1px solid #cecac8',
                fontSize: '11px',
              }}
            >
              <span style={{ color: '#767371', textTransform: 'uppercase', fontSize: '10px' }}>{key}:</span>
              <span style={{ color: '#242424', fontWeight: 600 }}>{val}</span>
            </div>
          ))}
        </div>
      )}

      {/* 4. Key Recommendations List */}
      {key_recommendations && key_recommendations.length > 0 && (
        <div
          style={{
            padding: '14px 16px',
            borderRadius: '16px',
            backgroundColor: '#ffffff',
            border: '1px solid #cecac8',
          }}
        >
          <span
            style={{
              fontSize: '10px',
              fontWeight: 600,
              color: '#767371',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            OPERATIONAL DIRECTIVES
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
            {key_recommendations.map((rec, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '8px',
                  fontSize: '12px',
                  color: '#242424',
                }}
              >
                <span style={{ color: '#2b59d1', fontSize: '12px', marginTop: '1px' }}>▸</span>
                <span style={{ lineHeight: 1.5 }}>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. Supporting Scientific Evidence Panel */}
      {evidence_summary && evidence_summary.length > 0 && (
        <EvidencePanel evidenceList={evidence_summary} />
      )}

      {/* 6. Context Action Buttons */}
      {visual_payload?.focus_zone_id && onFocusZone && (
        <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
          <button
            type="button"
            onClick={() => onFocusZone(visual_payload.focus_zone_id!)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              borderRadius: '100px',
              backgroundColor: '#2b59d1',
              color: '#f6f3f1',
              fontSize: '11px',
              fontWeight: 500,
              border: 'none',
              cursor: 'pointer',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              transition: 'opacity 0.15s ease',
            }}
          >
            <Compass size={13} />
            <span>HIGHLIGHT ON MAP ▸</span>
          </button>
        </div>
      )}
    </div>
  );
};
