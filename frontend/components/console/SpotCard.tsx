"use client";

import React from "react";
import { MessageSquareText, TriangleAlert, X } from "lucide-react";
import { motion } from "motion/react";
import { RESTRICTED } from "@/lib/marine/data";
import { offshoreKm, pointInRing } from "@/lib/marine/field";
import { bandOf } from "@/lib/marine/ramps";
import type { FieldKey, Sample } from "@/lib/marine/types";
import type { SpotEvent } from "./types";

interface SpotCardProps {
  spot: SpotEvent;
  sample: (key: FieldKey, lon: number, lat: number) => Sample;
  onClose: () => void;
  onSetHome: () => void;
  onAsk: () => void;
}

const CARD_W = 236;

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
  const top = Math.max(8, Math.min(spot.y - 60, spot.h - 270));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: 4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.14 }}
      className="absolute z-[700] rounded-xl border border-line bg-surface px-[13px] pb-[11px] pt-3 shadow-float"
      style={{
        left,
        top,
        width: CARD_W,
        backgroundColor: '#ffffff',
        border: '1px solid #d8e9ee',
        boxShadow: '0 14px 40px rgba(18, 49, 59, 0.18)',
      }}
      role="dialog"
      aria-label="Conditions at this spot"
    >
      <div className="mb-[7px] flex items-center gap-2">
        <span className="size-[11px] flex-none rounded" style={{ background: band.color }} />
        <span className="text-sm font-bold leading-tight text-ink">{band.name} water</span>
        <button onClick={onClose} className="ml-auto text-ink-3 hover:text-ink cursor-pointer" aria-label="Close">
          <X className="size-3.5" />
        </button>
      </div>
      <p className="mb-[9px] text-[11.5px] leading-[1.45] text-ink-2">{band.note.replace(/^[^—]*— /, "")}</p>
      {restricted && (
        <div className="mb-[9px] flex items-start gap-1.5 rounded-[7px] bg-[#FDECE9] px-2 py-[7px] text-[11px] leading-snug text-[#B3342A]">
          <TriangleAlert className="mt-px size-3.5 flex-none" />
          <span>Restricted marine sanctuary zone. Fishing prohibited here.</span>
        </div>
      )}
      <div className="mb-2.5 flex gap-[7px]">
        <Fact label="WAVE" value={`${wv.v.toFixed(1)} m`} />
        <Fact label="WIND" value={`${Math.round(wd.v * 3.6)} km/h`} />
        <Fact label="SHORE" value={shore < 1 ? "<1 km" : `${Math.round(shore)} km`} />
      </div>
      <div className="flex gap-1.5">
        <button
          onClick={onSetHome}
          className="flex-1 rounded-lg bg-[#087EA4] hover:bg-[#05627F] py-[7px] text-[11.5px] font-semibold text-white cursor-pointer transition-colors"
        >
          Set as position
        </button>
        <button
          onClick={onAsk}
          title="Ask AI about this spot"
          className="grid w-9 place-items-center rounded-lg border border-line text-[#087EA4] hover:bg-tint cursor-pointer transition-colors"
        >
          <MessageSquareText className="size-3.5" />
        </button>
      </div>
    </motion.div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 flex-1 rounded-[7px] border border-line bg-sea px-1.5 py-1.5">
      <div className="eyebrow text-[8px] text-ink-3">{label}</div>
      <div className="whitespace-nowrap font-mono text-[11.5px] font-bold tabular text-ink">{value}</div>
    </div>
  );
}
