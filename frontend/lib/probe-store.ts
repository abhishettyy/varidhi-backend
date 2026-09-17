import { useSyncExternalStore } from "react";
import type { FieldKey, Sample } from "./marine/types";

/**
 * Cursor readout. Mousemove fires at frame rate, so it lives outside React
 * state — only the footer readout subscribes, and nothing else re-renders.
 */
export interface Probe {
  lat: number;
  lon: number;
  key: FieldKey;
  sample: Sample;
}

let probe: Probe | null = null;
const subs = new Set<() => void>();

export function setProbe(p: Probe | null) {
  probe = p;
  subs.forEach((f) => f());
}

function subscribe(cb: () => void) {
  subs.add(cb);
  return () => {
    subs.delete(cb);
  };
}

export function useProbe(): Probe | null {
  return useSyncExternalStore(subscribe, () => probe, () => null);
}
