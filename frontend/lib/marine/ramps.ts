import type { FieldKey } from "./types";

export interface Ramp {
  name: string;
  short: string;
  unit: string;
  min: number;
  max: number;
  decimals: number;
  log?: boolean;
  stops: [number, string][];
}

export const RAMPS: Record<FieldKey, Ramp> = {
  waves: {
    name: "Significant wave height", short: "Wave", unit: "m", min: 0, max: 6, decimals: 1,
    stops: [[0, "#C9EDF6"], [0.5, "#8FDCEC"], [1, "#58C8DC"], [1.5, "#35B8C8"], [2, "#3FAF8F"],
      [2.5, "#8FCB63"], [3, "#F0C44E"], [3.8, "#FF9E62"], [4.6, "#FF7666"], [6, "#C2417A"]],
  },
  wind: {
    name: "Wind speed", short: "Wind", unit: "m/s", min: 0, max: 26, decimals: 0,
    stops: [[0, "#E8F6FB"], [3, "#A8DDEE"], [6, "#5CC3DF"], [9, "#2FA8C9"], [12, "#3FAF8F"],
      [15, "#97C95C"], [18, "#F0B93F"], [21, "#FF8A5B"], [24, "#E85A6B"], [26, "#B23FA0"]],
  },
  currents: {
    name: "Surface current", short: "Current", unit: "m/s", min: 0, max: 2, decimals: 2,
    stops: [[0, "#EAF7FA"], [0.25, "#B4E4EE"], [0.5, "#6FCBDD"], [0.8, "#2FA9C6"], [1.1, "#3FAF8F"],
      [1.5, "#F0C44E"], [2, "#FF7666"]],
  },
  sst: {
    name: "Sea surface temperature", short: "SST", unit: "°C", min: 19, max: 33, decimals: 1,
    stops: [[19, "#2E5FA3"], [22, "#3E93C6"], [25, "#4FC4C9"], [27, "#62C79A"], [29, "#C8CE5E"],
      [31, "#F2A64B"], [32.5, "#EE6E52"], [33, "#C2417A"]],
  },
  chl: {
    name: "Chlorophyll-a", short: "Chl-a", unit: "mg/m³", min: 0.03, max: 20, decimals: 2, log: true,
    stops: [[0.03, "#1F3E80"], [0.1, "#2C79B8"], [0.3, "#35B8C8"], [1, "#3FAF8F"], [3, "#A9CB55"],
      [8, "#F0C44E"], [20, "#FF7666"]],
  },
};

export const VECTOR_FIELDS = new Set<FieldKey>(["waves", "wind", "currents"]);

export interface Band {
  max: number;
  color: string;
  name: string;
  note: string;
}

/* Plain-language bands. The simple view paints only these four steps, so the
   sea reads as "fine / careful / rough / don't" instead of a rainbow you have
   to decode against a scale. */
export const BANDS: Record<FieldKey, { explain: string; arrows: string | null; steps: Band[] }> = {
  waves: {
    explain: "Colour shows how rough the sea is for a small boat.",
    arrows: "Arrows show which way the swell is running.",
    steps: [
      { max: 1.0, color: "#7FD0B6", name: "Calm", note: "Under 1 m — fine for small boats" },
      { max: 2.0, color: "#F5CE7A", name: "Moderate", note: "1–2 m — manageable, stay alert" },
      { max: 3.0, color: "#FF9C85", name: "Rough", note: "2–3 m — hard going in a small boat" },
      { max: 99, color: "#E0566C", name: "Dangerous", note: "Over 3 m — do not go out" },
    ],
  },
  wind: {
    explain: "Colour shows how hard the wind is blowing.",
    arrows: "Arrows show which way the wind is blowing.",
    steps: [
      { max: 5, color: "#7FD0B6", name: "Light", note: "Under 18 km/h — easy going" },
      { max: 10, color: "#F5CE7A", name: "Breezy", note: "18–36 km/h — choppy, spray over the bow" },
      { max: 15, color: "#FF9C85", name: "Strong", note: "36–54 km/h — hard to hold a heading" },
      { max: 99, color: "#E0566C", name: "Gale", note: "Over 54 km/h — stay in harbour" },
    ],
  },
  currents: {
    explain: "Colour shows how fast the water itself is moving.",
    arrows: "Arrows show which way the current is setting.",
    steps: [
      { max: 0.3, color: "#7FD0B6", name: "Weak", note: "Barely pushes the boat" },
      { max: 0.7, color: "#F5CE7A", name: "Noticeable", note: "Nets and lines will drift" },
      { max: 1.2, color: "#FF9C85", name: "Strong", note: "Costs fuel to hold position" },
      { max: 99, color: "#E0566C", name: "Very strong", note: "Hard to work in — avoid" },
    ],
  },
  sst: {
    explain: "Colour shows how warm the surface water is.",
    arrows: null,
    steps: [
      { max: 26, color: "#9FD4E8", name: "Cool", note: "Under 26 °C" },
      { max: 28, color: "#7FD0B6", name: "Mild", note: "26–28 °C — many species feed here" },
      { max: 30, color: "#F5CE7A", name: "Warm", note: "28–30 °C" },
      { max: 99, color: "#FF9C85", name: "Very warm", note: "Over 30 °C — fish go deeper" },
    ],
  },
  chl: {
    explain: "Colour shows where the plankton is — where the fish feed.",
    arrows: null,
    steps: [
      { max: 0.3, color: "#DCEAEF", name: "Poor", note: "Clear water, little feed" },
      { max: 1, color: "#A9D8C6", name: "Fair", note: "Some feed about" },
      { max: 3, color: "#6FC490", name: "Good", note: "Worth a look" },
      { max: 99, color: "#2F9E63", name: "Very rich", note: "Strong feeding ground" },
    ],
  },
};

export const SIMPLE_TITLE: Record<FieldKey, string> = {
  waves: "How rough the sea is",
  wind: "How hard the wind blows",
  currents: "How the water is moving",
  sst: "How warm the water is",
  chl: "Where the fish feed",
};

export function bandOf(key: FieldKey, v: number): Band & { i: number } {
  const s = BANDS[key].steps;
  for (let i = 0; i < s.length; i++) if (v < s[i].max) return { ...s[i], i };
  return { ...s[s.length - 1], i: s.length - 1 };
}

export function hexRgb(h: string): [number, number, number] {
  return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
}

export function normValue(key: FieldKey, v: number): number {
  const r = RAMPS[key];
  const t = r.log
    ? (Math.log(Math.max(r.min, v)) - Math.log(r.min)) / (Math.log(r.max) - Math.log(r.min))
    : (v - r.min) / (r.max - r.min);
  return Math.max(0, Math.min(1, t));
}

/** Value at fraction `t` (0–1) along the ramp, honouring log ramps. */
export function rampValueAt(key: FieldKey, t: number): number {
  const r = RAMPS[key];
  return r.log
    ? Math.exp(Math.log(r.min) + (Math.log(r.max) - Math.log(r.min)) * t)
    : r.min + (r.max - r.min) * t;
}

const lutCache: Partial<Record<FieldKey, Uint8ClampedArray>> = {};

export function rampLUT(key: FieldKey): Uint8ClampedArray {
  const cached = lutCache[key];
  if (cached) return cached;
  const r = RAMPS[key];
  const N = 256;
  const lut = new Uint8ClampedArray(N * 3);
  const stops = r.stops.map(([v, c]) => [normValue(key, v), hexRgb(c)] as const);
  for (let i = 0; i < N; i++) {
    const t = i / (N - 1);
    let a = stops[0];
    let b = stops[stops.length - 1];
    for (let s = 0; s < stops.length - 1; s++) {
      if (t >= stops[s][0] && t <= stops[s + 1][0]) { a = stops[s]; b = stops[s + 1]; break; }
    }
    const f = b[0] === a[0] ? 0 : (t - a[0]) / (b[0] - a[0]);
    lut[i * 3] = a[1][0] + (b[1][0] - a[1][0]) * f;
    lut[i * 3 + 1] = a[1][1] + (b[1][1] - a[1][1]) * f;
    lut[i * 3 + 2] = a[1][2] + (b[1][2] - a[1][2]) * f;
  }
  lutCache[key] = lut;
  return lut;
}

export function rampColor(key: FieldKey, v: number): string {
  const lut = rampLUT(key);
  const i = Math.round(normValue(key, v) * 255) * 3;
  return `rgb(${lut[i]},${lut[i + 1]},${lut[i + 2]})`;
}

export function formatValue(key: FieldKey, v: number): string {
  if (key === "chl") return v.toFixed(v < 1 ? 2 : 1);
  return v.toFixed(RAMPS[key].decimals);
}
