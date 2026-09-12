"use client";

import React from "react";
import { MapPin, Minus, Plus } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { BANDS, RAMPS, SIMPLE_TITLE, rampColor } from "@/lib/marine/ramps";
import type { FieldKey, LatLon } from "@/lib/marine/types";
import type { Conditions } from "./types";

/* Floating chart furniture. Everything here is positioned with inline styles
   on purpose: this project has no Tailwind build, so utility classes like
   `absolute top-3.5` are inert and the panels would fall into static flow
   underneath the map. Only classes defined in globals.css are used. */

interface MapHudProps {
  overlay: FieldKey;
  simple: boolean;
  particles: boolean;
  timeTag: string;
  home: LatLon;
  cond: Conditions;
  onLocate: () => void;
  onZoom: (d: number) => void;
}

const PANEL: React.CSSProperties = {
  backgroundColor: "#ffffff",
  border: "1px solid #d8e9ee",
  boxShadow: "0 4px 14px rgba(18, 49, 59, 0.09)",
};

export function MapHud({ overlay, simple, particles, timeTag, home, cond, onLocate, onZoom }: MapHudProps) {
  const r = RAMPS[overlay];
  const band = BANDS[overlay];
  const title = simple ? SIMPLE_TITLE[overlay] : r.name;
  const dot = simple ? band.steps[1].color : rampColor(overlay, (r.min + r.max) / 2);
  const explain = band.explain + (particles && band.arrows ? ` ${band.arrows}` : "");

  return (
    <>
      {/* Position pill */}
      <button
        onClick={onLocate}
        title="Recentre on your position"
        style={{
          ...PANEL,
          position: "absolute",
          left: 14,
          top: 14,
          zIndex: 600,
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "7px 12px 7px 10px",
          borderRadius: 9,
          cursor: "pointer",
          textAlign: "left",
        }}
      >
        <MapPin size={14} color="#ff7666" strokeWidth={2} style={{ flexShrink: 0 }} />
        <span>
          <span className="eyebrow" style={{ display: "block", color: "var(--color-ink-3)" }}>
            Your position
          </span>
          <span className="font-mono tabular" style={{ fontSize: 12.5, fontWeight: 600, color: "var(--color-ink)" }}>
            {home.lat.toFixed(3)}°N {home.lon.toFixed(3)}°E
          </span>
        </span>
      </button>

      {/* Layer title + one-line explanation */}
      <div
        className="map-hud-center"
        style={{
          position: "absolute",
          left: "50%",
          top: 14,
          transform: "translateX(-50%)",
          zIndex: 600,
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
          pointerEvents: "none",
        }}
      >
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={`${overlay}-${simple}`}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.16 }}
            style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}
          >
            <div
              style={{
                ...PANEL,
                display: "flex",
                alignItems: "center",
                gap: 9,
                padding: "7px 14px",
                borderRadius: 9999,
              }}
            >
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: dot, flexShrink: 0 }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: "var(--color-ink)" }}>{title}</span>
              <span className="font-mono" style={{ fontSize: 11, color: "var(--color-ink-3)" }}>{timeTag}</span>
            </div>
            <div
              style={{
                ...PANEL,
                maxWidth: 400,
                padding: "6px 14px",
                borderRadius: 16,
                textAlign: "center",
                fontSize: 12,
                lineHeight: 1.45,
                color: "var(--color-ink-2)",
              }}
            >
              {explain}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Zoom stack */}
      <div
        style={{
          ...PANEL,
          position: "absolute",
          right: 14,
          top: 14,
          zIndex: 600,
          display: "flex",
          flexDirection: "column",
          borderRadius: 9,
          overflow: "hidden",
        }}
      >
        <ZoomButton label="Zoom in" onClick={() => onZoom(1)}>
          <Plus size={16} />
        </ZoomButton>
        <ZoomButton label="Zoom out" onClick={() => onZoom(-1)} divider>
          <Minus size={16} />
        </ZoomButton>
      </div>

      {/* Live readings at the boat */}
      <div
        className="map-hud-readout"
        style={{
          ...PANEL,
          position: "absolute",
          right: 14,
          bottom: 34,
          zIndex: 600,
          width: 204,
          borderRadius: 10,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "9px 11px 8px 11px",
            borderBottom: "1px solid #d8e9ee",
          }}
        >
          <span className="eyebrow" style={{ color: "var(--color-ink-3)" }}>At your position</span>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: cond.state.color }} />
        </div>
        <CondRow label="WAVE" value={`${cond.wave.toFixed(1)} m`} />
        <CondRow label="SWELL DIR" value={`${cond.swell.name} ${cond.swell.deg}°`} />
        <CondRow label="WIND" value={`${cond.windKmh} km/h`} />
        <CondRow label="CURRENT" value={`${cond.current.toFixed(2)} m/s`} />
        <CondRow label="SST" value={`${cond.sst.toFixed(1)}°C`} />
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "8px 11px",
            borderTop: "1px solid #d8e9ee",
            backgroundColor: "var(--color-sea)",
          }}
        >
          <span className="font-mono" style={{ fontSize: 10.5, color: "var(--color-ink-3)" }}>SEA STATE</span>
          <span className="font-mono" style={{ fontSize: 11.5, fontWeight: 700, color: cond.state.color }}>
            {cond.state.name.toUpperCase()}
          </span>
        </div>
      </div>
    </>
  );
}

function ZoomButton({
  label, onClick, divider, children,
}: { label: string; onClick: () => void; divider?: boolean; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      title={label}
      aria-label={label}
      style={{
        display: "grid",
        placeItems: "center",
        width: 34,
        height: 34,
        border: "none",
        borderTop: divider ? "1px solid #d8e9ee" : "none",
        backgroundColor: "transparent",
        color: "var(--color-ink-2)",
        cursor: "pointer",
      }}
      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "var(--color-tint)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
    >
      {children}
    </button>
  );
}

function CondRow({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "7px 11px",
        borderTop: "1px solid #eef6f8",
      }}
    >
      <span className="font-mono" style={{ fontSize: 10.5, color: "var(--color-ink-3)" }}>{label}</span>
      <span className="font-mono tabular" style={{ fontSize: 13, fontWeight: 700, color: "var(--color-ink)" }}>{value}</span>
    </div>
  );
}
