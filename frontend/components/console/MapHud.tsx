"use client";

import React from "react";
import { MapPin, Minus, Plus } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { BANDS, RAMPS, SIMPLE_TITLE, rampColor } from "@/lib/marine/ramps";
import type { FieldKey, LatLon } from "@/lib/marine/types";
import type { Conditions } from "./types";

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

export function MapHud({ overlay, simple, particles, timeTag, home, cond, onLocate, onZoom }: MapHudProps) {
  const r = RAMPS[overlay];
  const band = BANDS[overlay];
  const title = simple ? SIMPLE_TITLE[overlay] : r.name;
  const dot = simple ? band.steps[1].color : rampColor(overlay, (r.min + r.max) / 2);
  const explain = band.explain + (particles && band.arrows ? ` ${band.arrows}` : "");

  return (
    <>
      <button
        onClick={onLocate}
        title="Use my GPS position"
        className="absolute left-3.5 top-3.5 z-[600] flex items-center gap-2.5 rounded-[9px] border border-line bg-surface py-[7px] pl-2.5 pr-3 shadow-card transition-colors hover:border-secondary cursor-pointer"
        style={{ backgroundColor: '#ffffff', border: '1px solid #d8e9ee' }}
      >
        <MapPin className="size-3.5 flex-none text-accent" style={{ color: '#ff7666' }} strokeWidth={2} />
        <span className="text-left">
          <span className="eyebrow block text-ink-3">Your position</span>
          <span className="font-mono text-[11.5px] font-semibold tabular text-ink">
            {home.lat.toFixed(3)}°N {home.lon.toFixed(3)}°E
          </span>
        </span>
      </button>

      <div className="pointer-events-none absolute left-1/2 top-3.5 z-[600] hidden -translate-x-1/2 flex-col items-center gap-2 md:flex">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={`${overlay}-${simple}`}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.16 }}
            className="flex flex-col items-center gap-2"
          >
            <div
              className="flex items-center gap-[9px] rounded-full border border-line bg-white/95 px-3.5 py-[7px] shadow-soft backdrop-blur"
              style={{ border: '1px solid #d8e9ee' }}
            >
              <span className="size-2 rounded-full" style={{ background: dot }} />
              <span className="text-[12.5px] font-semibold text-ink">{title}</span>
              <span className="font-mono text-[10.5px] text-ink-3">{timeTag}</span>
            </div>
            <div
              className="max-w-[380px] rounded-2xl border border-line bg-white/93 px-[13px] py-[5px] text-center text-[11.5px] leading-snug text-ink-2 shadow-soft"
              style={{ border: '1px solid #d8e9ee' }}
            >
              {explain}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <div
        className="absolute right-3.5 top-3.5 z-[600] flex flex-col overflow-hidden rounded-[9px] border border-line bg-surface shadow-card"
        style={{ backgroundColor: '#ffffff', border: '1px solid #d8e9ee' }}
      >
        <button onClick={() => onZoom(1)} title="Zoom in" className="grid size-8 place-items-center text-ink-2 hover:bg-tint hover:text-primary cursor-pointer">
          <Plus className="size-4" />
        </button>
        <button onClick={() => onZoom(-1)} title="Zoom out" className="grid size-8 place-items-center border-t border-line text-ink-2 hover:bg-tint hover:text-primary cursor-pointer">
          <Minus className="size-4" />
        </button>
      </div>

      <div
        className="absolute bottom-[34px] right-3.5 z-[600] hidden w-[196px] overflow-hidden rounded-card border border-line bg-surface shadow-card sm:block"
        style={{ backgroundColor: '#ffffff', border: '1px solid #d8e9ee', borderRadius: '10px' }}
      >
        <div className="flex items-center justify-between border-b border-line px-[11px] pb-2 pt-[9px]">
          <span className="eyebrow text-ink-3">At your position</span>
          <span className="size-1.5 rounded-full" style={{ background: cond.state.color }} />
        </div>
        <CondRow label="WAVE" value={`${cond.wave.toFixed(1)} m`} />
        <CondRow label="SWELL DIR" value={`${cond.swell.name} ${cond.swell.deg}°`} />
        <CondRow label="WIND" value={`${cond.windKmh} km/h`} />
        <CondRow label="CURRENT" value={`${cond.current.toFixed(2)} m/s`} />
        <CondRow label="SST" value={`${cond.sst.toFixed(1)}°C`} />
        <div className="flex items-center justify-between border-t border-line bg-sea px-[11px] py-[7px]">
          <span className="font-mono text-[10px] text-ink-3">SEA STATE</span>
          <span className="font-mono text-[11px] font-bold" style={{ color: cond.state.color }}>{cond.state.name.toUpperCase()}</span>
        </div>
      </div>
    </>
  );
}

function CondRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-line px-[11px] py-[7px] [&+&]:border-t">
      <span className="font-mono text-[10px] text-ink-3">{label}</span>
      <span className="font-mono text-[12.5px] font-bold tabular text-ink">{value}</span>
    </div>
  );
}
