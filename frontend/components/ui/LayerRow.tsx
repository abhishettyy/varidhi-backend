"use client";

import React from "react";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";

interface LayerRowProps {
  checked: boolean;
  label: string;
  swatch?: string;
  onClick: () => void;
  /** radio rows belong to a one-of group */
  radio?: boolean;
}

export function LayerRow({ checked, label, swatch, onClick, radio }: LayerRowProps) {
  return (
    <button
      type="button"
      role={radio ? "radio" : "checkbox"}
      aria-checked={checked}
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2.5 rounded-lg px-[9px] py-2 text-left transition-colors",
        checked ? "bg-tint" : "hover:bg-sea",
      )}
    >
      <span
        className={cn(
          "grid size-4 flex-none place-items-center border-[1.5px] transition-colors",
          radio ? "rounded-full" : "rounded-[4px]",
          checked ? "border-primary bg-primary" : "border-line-strong bg-surface",
        )}
      >
        <svg viewBox="0 0 24 24" className="size-2.5" aria-hidden>
          <motion.path
            d="m4 12.5 5 5L20 6.5"
            fill="none"
            stroke="#fff"
            strokeWidth={3.2}
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={false}
            animate={{ pathLength: checked ? 1 : 0, opacity: checked ? 1 : 0 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
          />
        </svg>
      </span>
      <span className={cn("flex-1 text-[12.5px] font-medium text-ink-2", checked && "font-semibold text-ink")}>{label}</span>
      {swatch && <span className="size-[9px] flex-none rounded-[3px]" style={{ background: swatch }} />}
    </button>
  );
}
