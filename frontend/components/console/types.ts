import type { FieldKey, LatLon, MarkerKey } from "@/lib/marine/types";

export type LiveStatus = { kind: "loading" } | { kind: "live"; issued: Date } | { kind: "offline" };

export type Tone = "danger" | "warn" | "info" | "success";

export interface ConsoleAlert {
  id: string;
  tone: Tone;
  title: string;
  body: string;
  action?: { label: string; overlay?: FieldKey; markers?: MarkerKey[] };
}

export interface Toast {
  id: string;
  tone: Tone;
  title: string;
  body?: string;
}

/** A tap on the chart: where, plus the container geometry to place the card. */
export interface SpotEvent extends LatLon {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface MapApi {
  zoomBy: (d: number) => void;
  panTo: (ll: LatLon, zoom?: number) => void;
}

export interface Conditions {
  wave: number;
  swell: { deg: number; name: string };
  windKmh: number;
  current: number;
  sst: number;
  state: { name: string; color: string };
}

export const TONE: Record<Tone, { fg: string; bg: string; dot: string }> = {
  danger: { fg: "#B4233B", bg: "#FBE3E7", dot: "#D6334C" },
  warn: { fg: "#A86B12", bg: "#FDF3E1", dot: "#E8A93C" },
  info: { fg: "#05627F", bg: "#E3F7F8", dot: "#35B8C8" },
  success: { fg: "#2A8A6E", bg: "#E6F6F0", dot: "#3FAF8F" },
};
