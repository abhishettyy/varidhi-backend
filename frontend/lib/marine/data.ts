import type { FieldKey, LatLon, MarkerKey } from "./types";

export const HOME_DEFAULT: LatLon = { lat: 18.9133, lon: 72.8342 };
export const MAP_CENTER: [number, number] = [18.95, 72.72];
export const MAP_BOUNDS: [[number, number], [number, number]] = [[18.42, 72.28], [19.58, 73.22]];

export interface Ground {
  id: number;
  lat: number;
  lon: number;
  /** PFZ match score, 0–100 */
  score: number;
  species: string;
}

export const GROUNDS: Ground[] = [
  { id: 1, lat: 18.75, lon: 72.569, score: 79, species: "Surmai · Paplet" },
  { id: 2, lat: 18.98, lon: 72.639, score: 75, species: "Surmai · Bombil" },
  { id: 3, lat: 18.86, lon: 72.599, score: 73, species: "Tarli · Paplet" },
  { id: 4, lat: 18.70, lon: 72.619, score: 66, species: "Bombil" },
  { id: 5, lat: 18.90, lon: 72.519, score: 64, species: "Paplet · Tarli" },
  { id: 6, lat: 19.09, lon: 72.649, score: 58, species: "Bombil" },
];

/** Port approach channel — closed to fishing craft 14:00–18:00. */
export const RESTRICTED: [number, number][] = [
  [18.911, 72.898], [18.921, 72.936], [18.885, 72.951], [18.848, 72.944], [18.853, 72.911], [18.877, 72.895],
];
export const RESTRICTED_LABEL = "Port approach channel · closed 14:00–18:00";

export interface RiskZone {
  level: "HIGH" | "MODERATE";
  color: string;
  ring: [number, number][];
}

export const RISK_ZONES: RiskZone[] = [
  { level: "HIGH", color: "#FF7666", ring: [[19.06, 72.44], [19.14, 72.53], [19.05, 72.60], [18.96, 72.52]] },
  { level: "MODERATE", color: "#E8A93C", ring: [[18.72, 72.44], [18.82, 72.50], [18.75, 72.60], [18.65, 72.53]] },
];

/** [lat, lon, heading°] */
export const VESSELS: [number, number, number][] = [
  [18.99, 72.60, 35], [18.80, 72.66, 120], [18.66, 72.62, 280], [19.06, 72.57, 75], [18.88, 72.48, 200],
];

export const CYCLONE = {
  lat: 18.62,
  lon: 72.36,
  radiusM: 26000,
  track: [[18.42, 72.16], [18.52, 72.26], [18.62, 72.36]] as [number, number][],
  label: "Depression · moving NNE",
};

export interface Harbour extends LatLon {
  name: string;
  area: string;
  /** alternative spellings people type */
  aliases?: string[];
}

export const HARBOURS: Harbour[] = [
  { name: "Sassoon Dock", area: "Colaba, Mumbai", lat: 18.9133, lon: 72.8342, aliases: ["mumbai", "colaba", "sassoon"] },
  { name: "Versova", area: "Andheri, Mumbai", lat: 19.14, lon: 72.785, aliases: ["andheri"] },
  { name: "Madh Island", area: "Malad, Mumbai", lat: 19.16, lon: 72.772, aliases: ["madh", "malad"] },
  { name: "Vasai", area: "Palghar", lat: 19.31, lon: 72.785, aliases: ["bassein"] },
  { name: "Alibag", area: "Raigad", lat: 18.64, lon: 72.855, aliases: ["alibaug"] },
  { name: "Revdanda", area: "Raigad", lat: 18.54, lon: 72.905 },
];

export const OVERLAYS: { key: FieldKey; label: string; swatch: string }[] = [
  { key: "waves", label: "Waves", swatch: "#35B8C8" },
  { key: "wind", label: "Wind", swatch: "#2FA8C9" },
  { key: "currents", label: "Currents", swatch: "#3FAF8F" },
  { key: "sst", label: "Sea temperature", swatch: "#F2A64B" },
  { key: "chl", label: "Chlorophyll", swatch: "#A9CB55" },
];

export const MARKER_LAYERS: { key: MarkerKey; label: string; swatch: string }[] = [
  { key: "pfz", label: "Fishing grounds", swatch: "#3FAF8F" },
  { key: "risk", label: "Risk zones", swatch: "#FF7666" },
  { key: "restricted", label: "Restricted water", swatch: "#D6334C" },
  { key: "cyclone", label: "Cyclone watch", swatch: "#E8A93C" },
  { key: "vessels", label: "Vessels", swatch: "#607D86" },
];

export function tierColor(score: number): string {
  return score >= 72 ? "#3FAF8F" : score >= 62 ? "#E8A93C" : "#FF7666";
}
