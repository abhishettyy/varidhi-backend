'use client';

import React, { useState, useEffect } from 'react';

interface PipelineNode {
  id: string;
  label: string;
  subtext: string;
  durationMs: number;
}

const PIPELINE_NODES: PipelineNode[] = [
  { id: 'understand_query', label: 'Parsing Query', subtext: 'LLM entity extraction & intent classification', durationMs: 600 },
  { id: 'planner', label: 'Planning Tools', subtext: 'Selecting required oceanographic data tools', durationMs: 500 },
  { id: 'tool_selection', label: 'Dispatching Tools', subtext: 'Routing to P4 marine data adapters', durationMs: 400 },
  { id: 'executor', label: 'Fetching Data', subtext: 'PFZ · SST · Wave · Wind · Tide · Restrictions', durationMs: 900 },
  { id: 'evidence_assembly', label: 'Assembling Evidence', subtext: 'P6 opportunity & risk scoring', durationMs: 700 },
  { id: 'response_generation', label: 'Generating Response', subtext: 'LLM formatting advisory narrative', durationMs: 600 },
];

interface PipelineStreamProps {
  isActive: boolean;
}

export const PipelineStream: React.FC<PipelineStreamProps> = ({ isActive }) => {
  const [activeNodeIndex, setActiveNodeIndex] = useState(-1);
  const [completedNodes, setCompletedNodes] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!isActive) {
      setActiveNodeIndex(-1);
      setCompletedNodes(new Set());
      return;
    }

    let currentIndex = 0;
    let elapsed = 0;

    const advance = () => {
      if (currentIndex >= PIPELINE_NODES.length) return;

      setActiveNodeIndex(currentIndex);

      const delay = PIPELINE_NODES[currentIndex].durationMs;
      elapsed += delay;

      const timeout = setTimeout(() => {
        setCompletedNodes((prev) => new Set([...prev, currentIndex]));
        currentIndex++;
        advance();
      }, delay);

      return timeout;
    };

    const firstTimeout = setTimeout(advance, 100);
    return () => clearTimeout(firstTimeout);
  }, [isActive]);

  if (!isActive) return null;

  return (
    <div
      style={{
        padding: '16px',
        borderRadius: '20px',
        backgroundColor: '#ffffff',
        border: '1px solid #cecac8',
        display: 'flex',
        flexDirection: 'column',
        gap: '0px',
        width: 'fit-content',
        maxWidth: '100%',
        boxShadow: '0 2px 12px rgba(43, 89, 209, 0.06)',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '14px',
        }}
      >
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: '#2b59d1',
            boxShadow: '0 0 0 3px rgba(43,89,209,0.15)',
            animation: 'varPulse 1.4s ease-in-out infinite',
          }}
        />
        <span
          style={{
            fontSize: '10px',
            fontWeight: 600,
            color: '#2b59d1',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
          }}
        >
          LangGraph Pipeline — Live
        </span>
      </div>

      {/* Nodes */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {PIPELINE_NODES.map((node, idx) => {
          const isCompleted = completedNodes.has(idx);
          const isRunning = activeNodeIndex === idx && !isCompleted;
          const isPending = activeNodeIndex < idx;

          return (
            <div
              key={node.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                padding: '8px 10px',
                borderRadius: '12px',
                backgroundColor: isRunning
                  ? 'rgba(43, 89, 209, 0.06)'
                  : isCompleted
                  ? 'transparent'
                  : 'transparent',
                transition: 'background-color 0.25s ease',
              }}
            >
              {/* Status indicator */}
              <div
                style={{
                  width: 18,
                  height: 18,
                  borderRadius: '50%',
                  flexShrink: 0,
                  marginTop: '1px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: isCompleted
                    ? '#2b59d1'
                    : isRunning
                    ? 'rgba(43,89,209,0.15)'
                    : 'rgba(206,202,200,0.4)',
                  border: isRunning
                    ? '1.5px solid #2b59d1'
                    : isCompleted
                    ? 'none'
                    : '1.5px solid #cecac8',
                  transition: 'all 0.25s ease',
                }}
              >
                {isCompleted && (
                  <svg width="9" height="7" viewBox="0 0 9 7" fill="none">
                    <path d="M1 3.5L3.5 6L8 1" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {isRunning && (
                  <div
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      backgroundColor: '#2b59d1',
                      animation: 'varPulse 0.8s ease-in-out infinite',
                    }}
                  />
                )}
              </div>

              {/* Connector line + text */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '12px',
                    fontWeight: isRunning ? 600 : isCompleted ? 500 : 400,
                    color: isCompleted ? '#242424' : isRunning ? '#2b59d1' : '#a8a29e',
                    lineHeight: 1.3,
                    transition: 'color 0.2s ease',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {node.label}
                  {isRunning && (
                    <span
                      style={{
                        display: 'inline-block',
                        marginLeft: '4px',
                        animation: 'varDots 1.4s steps(4, end) infinite',
                      }}
                    >
                      ...
                    </span>
                  )}
                </div>
                <div
                  style={{
                    fontSize: '10px',
                    color: isRunning ? 'rgba(43,89,209,0.65)' : '#c0bbb8',
                    marginTop: '1px',
                    transition: 'color 0.2s ease',
                  }}
                >
                  {node.subtext}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
