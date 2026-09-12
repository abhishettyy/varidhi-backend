"use client";

import React from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface SegmentedProps<T extends string> {
  value: T;
  options: { value: T; label: string; hint?: string }[];
  onChange: (v: T) => void;
  /** unique per control so the sliding pill doesn't jump between instances */
  id: string;
  className?: string;
}

export function Segmented<T extends string>({ value, options, onChange, id, className }: SegmentedProps<T>) {
  return (
    <div role="radiogroup" className={cn("flex gap-[3px] rounded-[9px] border border-line bg-sea p-[3px]", className)}>
      {options.map((o) => {
        const on = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={on}
            onClick={() => onChange(o.value)}
            className={cn("relative flex-1 rounded-[7px] py-[7px] text-xs font-semibold transition-colors", on ? "text-primary" : "text-ink-2 hover:text-ink")}
          >
            {on && (
              <motion.span
                layoutId={`seg-${id}`}
                className="absolute inset-0 rounded-[7px] bg-surface shadow-soft"
                transition={{ type: "spring", bounce: 0.18, duration: 0.35 }}
              />
            )}
            <span className="relative flex flex-col items-center leading-tight">
              {o.label}
              {o.hint && <span className="font-mono text-[8.5px] font-medium tracking-wide text-ink-3">{o.hint}</span>}
            </span>
          </button>
        );
      })}
    </div>
  );
}
