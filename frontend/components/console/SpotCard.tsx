"use client";

import React from "react";
import { MessageSquareText, TriangleAlert, X } from "lucide-react";
import { motion } from "motion/react";
import { RESTRICTED } from "@/lib/marine/data";
import { offshoreKm, pointInRing } from "@/lib/marine/field";
import { bandOf } from "@/lib/marine/ramps";
import type { FieldKey, Sample } from "@/lib/marine/types";
import type { SpotEvent } from "./types";

/* Positioned with inline styles: there is no Tailwind build in this project,
   so utility classes would be inert and the card would not float. */

interface SpotCardProps {
  spot: SpotEvent;
  sample: (key: FieldKey, lon: number, lat: number) => Sample;
  onClose: () => void;
  onSetHome: () => void;
  onAsk: () => void;
}

const CARD_W = 240;

/** "What is it like here?" — answered where you tapped. */
export function SpotCard({ spot, sample, onClose, onSetHome, onAsk }: SpotCardProps) {
  const wv = sample("waves", spot.lon, spot.lat);
  const wd = sample("wind", spot.lon, spot.lat);
  const band = bandOf("waves", wv.v);
  const shore = Math.max(0, offshoreKm(spot.lon, spot.lat));
  const restricted = pointInRing(spot.lat, spot.lon, RESTRICTED);

  let x = spot.x + 14;
  if (x + CARD_W + 16 > spot.w) x = spot.x - CARD_W - 14;
  const left = Math.max(8, x);
  const top = Math.max(8, Math.min(spot.y - 60, spot.h - 280));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: 4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.14 }}
      style={{
        position: "absolute",
        left,
        top,
        width: CARD_W,
        zIndex: 700,
        padding: "12px 13px 11px 13px",
        borderRadius: 12,
        backgroundColor: "#ffffff",
        border: "1px solid #d8e9ee",
        boxShadow: "0 14px 40px rgba(18, 49, 59, 0.18)",
      }}
      role="dialog"
      aria-label="Conditions at this spot"
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
        <span style={{ width: 11, height: 11, borderRadius: 3, background: band.color, flexShrink: 0 }} />
        <span style={{ fontSize: 14, fontWeight: 700, lineHeight: 1.2, color: "var(--color-ink)" }}>
          {band.name} water
        </span>
        <button
          onClick={onClose}
          aria-label="Close"
          style={{
            marginLeft: "auto",
            border: "none",
            background: "transparent",
            color: "var(--color-ink-3)",
            cursor: "pointer",
            display: "grid",
            placeItems: "center",
          }}
        >
          <X size={14} />
        </button>
      </div>

      <p style={{ marginBottom: 9, fontSize: 12, lineHeight: 1.45, color: "var(--color-ink-2)" }}>
        {band.note.replace(/^[^—]*— /, "")}
      </p>

      {restricted && (
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: 6,
            marginBottom: 9,
            padding: "7px 8px",
            borderRadius: 7,
            backgroundColor: "#FDECE9",
            color: "#B3342A",
            fontSize: 11.5,
            lineHeight: 1.35,
          }}
        >
          <TriangleAlert size={14} style={{ flexShrink: 0, marginTop: 1 }} />
          <span>Port approach corridor — static nets and artisanal fishing prohibited.</span>
        </div>
      )}

      <div style={{ display: "flex", gap: 7, marginBottom: 10 }}>
        <Fact label="WAVE" value={`${wv.v.toFixed(1)} m`} />
        <Fact label="WIND" value={`${Math.round(wd.v * 3.6)} km/h`} />
        <Fact label="SHORE" value={shore < 1 ? "<1 km" : `${Math.round(shore)} km`} />
      </div>

      <div style={{ display: "flex", gap: 6 }}>
        <button
          onClick={onSetHome}
          style={{
            flex: 1,
            padding: "8px 10px",
            borderRadius: 8,
            border: "none",
            backgroundColor: "#087EA4",
            color: "#ffffff",
            fontSize: 12,
            fontWeight: 600,
            cursor: "pointer",
            transition: "background-color 0.15s ease",
          }}
          onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "#05627F"; }}
          onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "#087EA4"; }}
        >
          Set as position
        </button>
        <button
          onClick={onAsk}
          title="Ask the assistant about this spot"
          style={{
            width: 36,
            display: "grid",
            placeItems: "center",
            borderRadius: 8,
            border: "1px solid #d8e9ee",
            backgroundColor: "#ffffff",
            color: "#087EA4",
            cursor: "pointer",
          }}
        >
          <MessageSquareText size={14} />
        </button>
      </div>
    </motion.div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        flex: 1,
        minWidth: 0,
        padding: "6px 7px",
        borderRadius: 7,
        border: "1px solid #d8e9ee",
        backgroundColor: "var(--color-sea)",
      }}
    >
      <div className="eyebrow" style={{ fontSize: 9, color: "var(--color-ink-3)" }}>{label}</div>
      <div
        className="font-mono tabular"
        style={{ fontSize: 12, fontWeight: 700, whiteSpace: "nowrap", color: "var(--color-ink)" }}
      >
        {value}
      </div>
    </div>
  );
}
