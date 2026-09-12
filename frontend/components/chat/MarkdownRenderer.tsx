'use client';

import React from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

// ── Inline token renderer ──────────────────────────────────────────
function renderInline(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  // Patterns: **bold**, *italic*, `code`, [link](url)
  const pattern = /(\*\*(.+?)\*\*|\*(.+?)\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\))/g;
  let last = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > last) {
      parts.push(text.slice(last, match.index));
    }

    if (match[2]) {
      // **bold**
      parts.push(<strong key={match.index} style={{ fontWeight: 600, color: '#242424' }}>{match[2]}</strong>);
    } else if (match[3]) {
      // *italic*
      parts.push(<em key={match.index} style={{ fontStyle: 'italic' }}>{match[3]}</em>);
    } else if (match[4]) {
      // `code`
      parts.push(
        <code
          key={match.index}
          style={{
            fontFamily: 'var(--font-abc-diatype-mono), monospace',
            fontSize: '11px',
            backgroundColor: '#eeecea',
            padding: '1px 5px',
            borderRadius: '4px',
            color: '#2b59d1',
          }}
        >
          {match[4]}
        </code>
      );
    } else if (match[5] && match[6]) {
      // [link](url)
      parts.push(
        <a
          key={match.index}
          href={match[6]}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#2b59d1', textDecoration: 'underline' }}
        >
          {match[5]}
        </a>
      );
    }

    last = match.index + match[0].length;
  }

  if (last < text.length) {
    parts.push(text.slice(last));
  }

  return parts.length > 0 ? parts : [text];
}

// ── Table renderer ─────────────────────────────────────────────────
function renderTable(lines: string[], key: number): React.ReactNode {
  const rows = lines.map((l) =>
    l
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map((c) => c.trim())
  );

  // Filter out separator rows (--- lines)
  const headerRow = rows[0];
  const dataRows = rows.slice(1).filter((r) => !r.every((c) => /^[-:]+$/.test(c)));

  return (
    <div key={key} style={{ overflowX: 'auto', margin: '10px 0' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '12px',
          fontFamily: 'var(--font-sans)',
        }}
      >
        <thead>
          <tr>
            {headerRow.map((cell, ci) => (
              <th
                key={ci}
                style={{
                  padding: '7px 12px',
                  textAlign: 'left',
                  fontWeight: 600,
                  fontSize: '11px',
                  color: '#242424',
                  backgroundColor: '#eeecea',
                  borderBottom: '1px solid #cecac8',
                  whiteSpace: 'nowrap',
                  letterSpacing: '0.01em',
                }}
              >
                {renderInline(cell)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, ri) => (
            <tr
              key={ri}
              style={{ backgroundColor: ri % 2 === 0 ? '#ffffff' : '#f9f7f5' }}
            >
              {row.map((cell, ci) => (
                <td
                  key={ci}
                  style={{
                    padding: '6px 12px',
                    borderBottom: '1px solid #f0eeed',
                    color: '#4e4d4d',
                    lineHeight: 1.5,
                    verticalAlign: 'top',
                  }}
                >
                  {renderInline(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Code block renderer ────────────────────────────────────────────
function renderCodeBlock(code: string, lang: string, key: number): React.ReactNode {
  return (
    <div
      key={key}
      style={{
        margin: '10px 0',
        borderRadius: '10px',
        overflow: 'hidden',
        border: '1px solid #e0dedc',
      }}
    >
      {lang && (
        <div
          style={{
            padding: '4px 12px',
            backgroundColor: '#eeecea',
            fontSize: '10px',
            color: '#767371',
            fontFamily: 'var(--font-abc-diatype-mono), monospace',
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            borderBottom: '1px solid #e0dedc',
          }}
        >
          {lang}
        </div>
      )}
      <pre
        style={{
          padding: '12px 14px',
          backgroundColor: '#1e1e1e',
          color: '#d4d4d4',
          fontFamily: 'var(--font-abc-diatype-mono), monospace',
          fontSize: '11px',
          lineHeight: 1.6,
          overflowX: 'auto',
          margin: 0,
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
}

// ── Main parser ────────────────────────────────────────────────────
export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className,
}) => {
  const nodes: React.ReactNode[] = [];
  const lines = content.split('\n');
  let i = 0;
  let nodeKey = 0;

  while (i < lines.length) {
    const line = lines[i];

    // ── Fenced code block ─────────────────────────
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      nodes.push(renderCodeBlock(codeLines.join('\n'), lang, nodeKey++));
      i++; // skip closing ```
      continue;
    }

    // ── Table ─────────────────────────────────────
    if (line.startsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].startsWith('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      nodes.push(renderTable(tableLines, nodeKey++));
      continue;
    }

    // ── Headings ──────────────────────────────────
    const h3 = line.match(/^### (.+)/);
    const h2 = line.match(/^## (.+)/);
    const h1 = line.match(/^# (.+)/);

    if (h1) {
      nodes.push(
        <h1
          key={nodeKey++}
          style={{
            fontFamily: 'var(--font-untitled-serif), Georgia, serif',
            fontSize: '20px',
            fontWeight: 400,
            letterSpacing: '-0.02em',
            color: '#242424',
            margin: '16px 0 8px',
            lineHeight: 1.25,
          }}
        >
          {renderInline(h1[1])}
        </h1>
      );
      i++;
      continue;
    }

    if (h2) {
      nodes.push(
        <h2
          key={nodeKey++}
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '14px',
            fontWeight: 700,
            color: '#242424',
            margin: '14px 0 6px',
            letterSpacing: '-0.01em',
            lineHeight: 1.3,
          }}
        >
          {renderInline(h2[1])}
        </h2>
      );
      i++;
      continue;
    }

    if (h3) {
      nodes.push(
        <h3
          key={nodeKey++}
          style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '12px',
            fontWeight: 700,
            color: '#4e4d4d',
            margin: '10px 0 4px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
          }}
        >
          {renderInline(h3[1])}
        </h3>
      );
      i++;
      continue;
    }

    // ── Horizontal rule ───────────────────────────
    if (/^---+$/.test(line.trim())) {
      nodes.push(
        <hr
          key={nodeKey++}
          style={{ border: 'none', borderTop: '1px solid #e0dedc', margin: '10px 0' }}
        />
      );
      i++;
      continue;
    }

    // ── Unordered list ────────────────────────────
    if (/^[-*+] /.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*+] /.test(lines[i])) {
        items.push(lines[i].replace(/^[-*+] /, ''));
        i++;
      }
      nodes.push(
        <ul
          key={nodeKey++}
          style={{
            paddingLeft: '16px',
            margin: '6px 0',
            display: 'flex',
            flexDirection: 'column',
            gap: '3px',
          }}
        >
          {items.map((item, idx) => (
            <li
              key={idx}
              style={{
                fontSize: '13px',
                color: '#4e4d4d',
                lineHeight: 1.55,
                listStyleType: 'none',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
              }}
            >
              <span style={{ color: '#2b59d1', flexShrink: 0, marginTop: '2px' }}>▸</span>
              <span>{renderInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // ── Ordered list ──────────────────────────────
    if (/^\d+\. /.test(line)) {
      const items: string[] = [];
      let num = 1;
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\. /, ''));
        i++;
        num++;
      }
      nodes.push(
        <ol
          key={nodeKey++}
          style={{ paddingLeft: '20px', margin: '6px 0', display: 'flex', flexDirection: 'column', gap: '3px' }}
        >
          {items.map((item, idx) => (
            <li
              key={idx}
              style={{ fontSize: '13px', color: '#4e4d4d', lineHeight: 1.55 }}
            >
              {renderInline(item)}
            </li>
          ))}
        </ol>
      );
      void num;
      continue;
    }

    // ── Blockquote ────────────────────────────────
    if (line.startsWith('> ')) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].startsWith('> ')) {
        quoteLines.push(lines[i].slice(2));
        i++;
      }
      nodes.push(
        <blockquote
          key={nodeKey++}
          style={{
            borderLeft: '3px solid #2b59d1',
            paddingLeft: '12px',
            margin: '8px 0',
            color: '#767371',
            fontSize: '13px',
            fontStyle: 'italic',
            lineHeight: 1.5,
          }}
        >
          {quoteLines.map((q, qi) => (
            <p key={qi} style={{ margin: '2px 0' }}>{renderInline(q)}</p>
          ))}
        </blockquote>
      );
      continue;
    }

    // ── Empty line → spacer ───────────────────────
    if (line.trim() === '') {
      // Only add spacer if last node wasn't already a spacer
      if (nodes.length > 0) {
        nodes.push(<div key={nodeKey++} style={{ height: '6px' }} />);
      }
      i++;
      continue;
    }

    // ── Plain paragraph ───────────────────────────
    nodes.push(
      <p
        key={nodeKey++}
        style={{
          fontSize: '13px',
          color: '#4e4d4d',
          lineHeight: 1.65,
          margin: '2px 0',
        }}
      >
        {renderInline(line)}
      </p>
    );
    i++;
  }

  return (
    <div
      className={className}
      style={{
        fontFamily: 'var(--font-sans)',
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
        width: '100%',
      }}
    >
      {nodes}
    </div>
  );
};
