import React from "react";
import { cn } from "@/lib/utils";

/** Text with a light sweeping across it — for "working on it" states. */
export function ShimmerText({ children, className }: { children: React.ReactNode; className?: string }) {
  return <span className={cn("shimmer-text", className)}>{children}</span>;
}
