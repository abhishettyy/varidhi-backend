import React from "react";

export interface SeriesPoint {
  label: string;
  value: number;
}

export interface SeriesChart {
  title: string;
  unit: string;
  points: SeriesPoint[];
  threshold?: { value: number; label: string };
}

const W = 300, H = 60, PAD = 4;

export function Sparkline({ chart }: { chart: SeriesChart }) {
  const pts = chart.points;
  if (pts.length < 2) return null;
  const vals = pts.map((p) => p.value);
  const max = Math.max(...vals, chart.threshold?.value ?? 0) * 1.15 || 1;
  const x = (i: number) => PAD + (i * (W - 2 * PAD)) / (pts.length - 1);
  const y = (v: number) => H - PAD - (v / max) * (H - 2 * PAD);
  const line = pts.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(" ");
  const area = `${line} L${x(pts.length - 1)},${H} L${x(0)},${H} Z`;
  const peak = vals.indexOf(Math.max(...vals));
  const mid = Math.floor((pts.length - 1) / 2);

  return (
    <figure className="rounded-lg border border-line bg-sea px-2.5 pb-1.5 pt-2">
      <figcaption className="mb-1 flex items-baseline justify-between">
        <span className="eyebrow">{chart.title}</span>
        <span className="font-mono text-[10px] text-ink-2">
          peak <b className="text-ink">{vals[peak].toFixed(1)} {chart.unit}</b> @ {pts[peak].label}
        </span>
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="h-14 w-full" role="img" aria-label={chart.title}>
        <defs>
          <linearGradient id="spark-fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#35B8C8" stopOpacity="0.28" />
            <stop offset="100%" stopColor="#35B8C8" stopOpacity="0" />
          </linearGradient>
        </defs>
        {chart.threshold && (
          <line
            x1={0} x2={W} y1={y(chart.threshold.value)} y2={y(chart.threshold.value)}
            stroke="#FF7666" strokeWidth={1} strokeDasharray="4 4" vectorEffect="non-scaling-stroke"
          />
        )}
        <path d={area} fill="url(#spark-fill)" />
        <path d={line} fill="none" stroke="#087EA4" strokeWidth={1.8} strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
      </svg>
      <div className="mt-0.5 flex justify-between font-mono text-[9px] text-ink-3">
        <span>{pts[0].label}</span>
        {chart.threshold && <span className="text-accent">— {chart.threshold.value} {chart.unit} {chart.threshold.label}</span>}
        <span className="hidden sm:inline">{pts[mid].label}</span>
        <span>{pts[pts.length - 1].label}</span>
      </div>
    </figure>
  );
}
