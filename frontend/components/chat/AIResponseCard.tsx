'use client';

import React from 'react';
import { AgentResponseData } from '@/types/chat';
import { EvidencePanel } from './EvidencePanel';
import { MarkdownRenderer } from './MarkdownRenderer';
import { Compass, CheckCircle2, AlertTriangle, ShieldCheck, Activity, Cpu } from 'lucide-react';

interface AIResponseCardProps {
  data: AgentResponseData;
  onFocusZone?: (zoneId: string) => void;
  onViewLayer?: (layerKey: string) => void;
}

export const AIResponseCard: React.FC<AIResponseCardProps> = ({
  data,
  onFocusZone,
}) => {
  const {
    decision,
    safety_alert,
    key_recommendations,
    evidence_summary,
    visual_payload,
    markdown_content,
    telemetry,
    disclaimer,
  } = data;

  const focusZone = visual_payload?.focus_zone_id || decision?.selected_zone_id;

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
      {/* 1. Authoritative Deterministic Decision Hero Card */}
      {decision && (
        <div
          style={{
            padding: '16px',
            borderRadius: '18px',
            backgroundColor: decision.status === 'SELECTED' ? '#ffffff' : 'rgba(255, 148, 115, 0.08)',
            border: decision.status === 'SELECTED' ? '1px solid #2b59d1' : '1px solid #ff9473',
            boxShadow: '0 2px 10px rgba(36, 36, 36, 0.04)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          {/* Header with Zone ID & Decision Badge */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  backgroundColor: decision.status === 'SELECTED' ? '#cfdaf5' : '#fed7aa',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: decision.status === 'SELECTED' ? '#2b59d1' : '#c2410c',
                }}
              >
                {decision.status === 'SELECTED' ? <ShieldCheck size={14} /> : <AlertTriangle size={14} />}
              </div>
              <div>
                <span style={{ fontSize: '10px', color: '#767371', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block' }}>
                  P6 DECISION ENGINE VERDICT
                </span>
                <span style={{ fontSize: '14px', fontWeight: 600, color: '#242424' }}>
                  {decision.selected_zone_id ? `${decision.selected_zone_id.replace('_', ' ')}` : 'REGIONAL ADVISORY'}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 10px',
                  borderRadius: '9999px',
                  fontSize: '11px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  backgroundColor: decision.status === 'SELECTED' ? '#2b59d1' : '#ff9473',
                  color: '#ffffff',
                }}
              >
                {decision.status === 'SELECTED' ? 'CERTIFIED DESTINATION' : decision.status}
              </span>
            </div>
          </div>

          {/* Key Metric Score Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(85px, 1fr))',
              gap: '8px',
              backgroundColor: '#f6f3f1',
              padding: '10px 12px',
              borderRadius: '12px',
              border: '1px solid #cecac8',
            }}
          >
            <div>
              <span style={{ fontSize: '9px', color: '#767371', textTransform: 'uppercase', display: 'block' }}>Catch Opp</span>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#2b59d1' }}>{decision.opportunity_score}/100</span>
            </div>
            <div>
              <span style={{ fontSize: '9px', color: '#767371', textTransform: 'uppercase', display: 'block' }}>Marine Risk</span>
              <span style={{ fontSize: '13px', fontWeight: 600, color: (decision.risk_score ?? 0) > 50 ? '#c2410c' : '#15803d' }}>
                {decision.risk_score ?? '—'}/100
              </span>
            </div>
            {decision.ranking_score !== undefined && (
              <div>
                <span style={{ fontSize: '9px', color: '#767371', textTransform: 'uppercase', display: 'block' }}>Rank Score</span>
                <span style={{ fontSize: '13px', fontWeight: 600, color: '#242424' }}>{decision.ranking_score.toFixed(1)}/100</span>
              </div>
            )}
            <div>
              <span style={{ fontSize: '9px', color: '#767371', textTransform: 'uppercase', display: 'block' }}>Distance</span>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#242424' }}>
                {decision.distance_nm} NM {decision.bearing}
              </span>
            </div>
            <div>
              <span style={{ fontSize: '9px', color: '#767371', textTransform: 'uppercase', display: 'block' }}>Legal Check</span>
              <span style={{ fontSize: '12px', fontWeight: 600, color: decision.regulatory_status === 'ELIGIBLE' ? '#15803d' : '#b91c1c' }}>
                {decision.regulatory_status}
              </span>
            </div>
          </div>

          {/* Species Target Chips */}
          {decision.species && decision.species.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '10px', color: '#767371', textTransform: 'uppercase' }}>Target Species:</span>
              {decision.species.map((sp, idx) => (
                <span
                  key={idx}
                  style={{
                    padding: '2px 8px',
                    borderRadius: '9999px',
                    backgroundColor: '#ffffff',
                    border: '1px solid #cecac8',
                    fontSize: '11px',
                    color: '#242424',
                    fontWeight: 500,
                  }}
                >
                  {sp}
                </span>
              ))}
            </div>
          )}

          {/* Verification Reasons */}
          {decision.reasons && decision.reasons.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '2px' }}>
              <span style={{ fontSize: '10px', color: '#767371', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600 }}>
                Verification Gates:
              </span>
              {decision.reasons.map((r, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '6px', fontSize: '11px', color: '#242424' }}>
                  <CheckCircle2 size={12} style={{ color: '#2b59d1', marginTop: '2px', flexShrink: 0 }} />
                  <span style={{ lineHeight: 1.4 }}>{r}</span>
                </div>
              ))}
            </div>
          )}

          {/* Direct Action Directive */}
          {decision.action_advice && (
            <div
              style={{
                padding: '8px 12px',
                borderRadius: '10px',
                backgroundColor: 'rgba(43, 89, 209, 0.08)',
                border: '1px solid rgba(43, 89, 209, 0.2)',
                fontSize: '11px',
                color: '#2b59d1',
                fontWeight: 500,
              }}
            >
              ▸ Directive: {decision.action_advice}
            </div>
          )}
        </div>
      )}

      {/* 2. Safety Alert Banner if present & not duplicate of decision */}
      {safety_alert && !decision && (
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
            <span style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: '#c2410c' }}>{safety_alert.severity.replace('_', ' ')}</span>
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

      {/* 3. Markdown Content */}
      {markdown_content && (
        <MarkdownRenderer content={markdown_content} />
      )}

      {/* 4. Metric Badges Row */}
      {visual_payload?.metric_badges && Object.keys(visual_payload.metric_badges).length > 0 && (
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

      {/* 5. Key Recommendations List */}
      {key_recommendations && key_recommendations.length > 0 && !decision && (
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

      {/* 6. Supporting Scientific Evidence Panel */}
      {evidence_summary && evidence_summary.length > 0 && (
        <EvidencePanel evidenceList={evidence_summary} />
      )}

      {/* 7. Context Action Buttons */}
      {focusZone && onFocusZone && (
        <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
          <button
            type="button"
            onClick={() => onFocusZone(focusZone)}
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
            <span>HIGHLIGHT {focusZone.replace('_', ' ')} ON MAP ▸</span>
          </button>
        </div>
      )}

      {/* 8. Telemetry and Synthetic Data Disclaimer Footnote */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          paddingTop: '8px',
          borderTop: '1px solid #e0dedc',
          marginTop: '6px',
        }}
      >
        {telemetry && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '10px',
              color: '#767371',
              letterSpacing: '0.02em',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Cpu size={11} style={{ color: '#2b59d1' }} />
              <span>
                Model: <strong>{telemetry.llm_provider || 'Deterministic Engine'}</strong>
              </span>
              {telemetry.parser_mode && (
                <span>• Parser: {telemetry.parser_mode}</span>
              )}
            </div>
            {telemetry.total_pipeline_ms !== undefined && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Activity size={11} style={{ color: '#15803d' }} />
                <span>{Math.round(telemetry.total_pipeline_ms)}ms</span>
              </div>
            )}
          </div>
        )}

        {disclaimer && (
          <div
            style={{
              fontSize: '10px',
              color: '#a8a29e',
              fontStyle: 'italic',
              lineHeight: 1.3,
            }}
          >
            {disclaimer}
          </div>
        )}
      </div>
    </div>
  );
};
