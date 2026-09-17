/* =====================================================================
   Ocean field model.
   Live data comes from Open-Meteo Marine + Forecast (keyless, CORS-open),
   pulled as a coarse grid and interpolated. When the network is down, a
   synthetic-but-structured model (divergence-free flow + smooth scalar
   fields) stands in so the console still runs offline.
   ===================================================================== */
import { COAST_MAIN } from "./coast";
import type { FieldKey, LatLon, Sample } from "./types";

// ------------------------------------------------------------ geometry
// Coast line as a lat -> westernmost-longitude table, so "distance from
// shore" is cheap for every sample (chlorophyll, wave shoaling, SST).
const coastTable = (() => {
  const step = 0.01, lat0 = 17.9, lat1 = 20.1;
  const n = Math.round((lat1 - lat0) / step) + 1;
  const arr = new Float32Array(n).fill(73.6);
  for (const [la, lo] of COAST_MAIN) {
    const i = Math.round((la - lat0) / step);
    if (i >= 0 && i < n && lo < arr[i]) arr[i] = lo;
  }
  for (let pass = 0; pass < 6; pass++) {
    for (let i = 1; i < n - 1; i++) arr[i] = Math.min(arr[i], (arr[i - 1] + arr[i + 1]) / 2 + 0.02);
    for (let i = n - 2; i > 0; i--) arr[i] = Math.min(arr[i], (arr[i - 1] + arr[i + 1]) / 2 + 0.02);
  }
  return { lat0, step, n, arr };
})();

export function coastLon(lat: number): number {
  // linear interpolation between bins — rounding here shows up as horizontal
  // banding across the whole field once it's magnified on screen
  const f = (lat - coastTable.lat0) / coastTable.step;
  const i = Math.max(0, Math.min(coastTable.n - 2, Math.floor(f)));
  const w = Math.max(0, Math.min(1, f - i));
  return coastTable.arr[i] * (1 - w) + coastTable.arr[i + 1] * w;
}

/** Rough km offshore (positive = out to sea). */
export function offshoreKm(lon: number, lat: number): number {
  return (coastLon(lat) - lon) * 111 * 0.95;
}

export function haversineKm(la1: number, lo1: number, la2: number, lo2: number): number {
  const R = 6371, rad = (d: number) => (d * Math.PI) / 180;
  const dLa = rad(la2 - la1), dLo = rad(lo2 - lo1);
  const a = Math.sin(dLa / 2) ** 2 + Math.cos(rad(la1)) * Math.cos(rad(la2)) * Math.sin(dLo / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

/** Initial great-circle bearing from a to b, degrees clockwise from north. */
export function bearingDeg(a: LatLon, b: LatLon): number {
  const rad = (d: number) => (d * Math.PI) / 180;
  const y = Math.sin(rad(b.lon - a.lon)) * Math.cos(rad(b.lat));
  const x = Math.cos(rad(a.lat)) * Math.sin(rad(b.lat)) -
    Math.sin(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.cos(rad(b.lon - a.lon));
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
}

const COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
export function compassName(deg: number): string {
  return COMPASS[Math.round((((deg % 360) + 360) % 360) / 22.5) % 16];
}

/** Direction a vector is coming *from*, given its direction of travel. */
export function compass(u: number, w: number): { deg: number; name: string } {
  const toward = ((Math.atan2(u, w) * 180) / Math.PI + 360) % 360;
  const from = (toward + 180) % 360;
  return { deg: Math.round(from), name: compassName(from) };
}

export function pointInRing(lat: number, lon: number, ring: [number, number][]): boolean {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [yi, xi] = ring[i], [yj, xj] = ring[j];
    if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

export function seaState(v: number): { name: string; color: string } {
  if (v < 0.5) return { name: "Calm", color: "#3FAF8F" };
  if (v < 1.25) return { name: "Slight", color: "#3FAF8F" };
  if (v < 2) return { name: "Moderate", color: "#E8A93C" };
  if (v < 3) return { name: "Rough", color: "#FF7666" };
  return { name: "Very rough", color: "#D6334C" };
}

// ------------------------------------------------------ synthetic model
/* Components at mixed orientations: a single dominant direction made the
   banded view read as diagonal stripes rather than patches of water. */
function noise(x: number, y: number, t: number): number {
  return (0.92 * Math.sin(1.70 * x + 0.42 * y + t * 0.31)
    + 0.80 * Math.cos(-0.61 * x + 1.62 * y - t * 0.21)
    + 0.55 * Math.sin(2.41 * x - 1.93 * y + t * 0.44)
    + 0.45 * Math.cos(1.12 * x + 2.63 * y - t * 0.27)
    + 0.32 * Math.sin(3.31 * x + 2.94 * y + t * 0.61)
    + 0.30 * Math.cos(2.83 * x - 3.41 * y + t * 0.50)) / 3.34;
}

/** Stream function -> divergence-free flow, so eddies look like real water. */
function flowAt(lon: number, lat: number, t: number) {
  const x = (lon - 72.7) * 3.4, y = (lat - 18.95) * 3.4, h = 0.02;
  const dpdy = (noise(x, y + h, t) - noise(x, y - h, t)) / (2 * h);
  const dpdx = (noise(x + h, y, t) - noise(x - h, y, t)) / (2 * h);
  // mean south-west monsoon drift plus eddy field
  const u = 0.62 + 0.55 * dpdy;
  const v = 0.46 - 0.55 * dpdx;
  const m = Math.hypot(u, v) || 1;
  return { m, dirU: u / m, dirV: v / m };
}

const clamp01 = (x: number) => Math.max(0, Math.min(1, x));

export function sampleSynthetic(key: FieldKey, lon: number, lat: number, t: number): Sample {
  const off = offshoreKm(lon, lat);
  const f = flowAt(lon, lat, t);
  const shelter = clamp01(off / 26); // waves build offshore
  if (key === "wind") {
    const s = 2.5 + 11.0 * clamp01((f.m - 0.35) / 1.05) + 2.0 * shelter;
    return { v: s, u: f.dirU, w: f.dirV };
  }
  if (key === "currents") {
    const a = Math.atan2(f.dirV, f.dirU) + 0.42; // Ekman veer
    const s = 0.06 + 1.30 * clamp01((f.m - 0.38) / 1.0) * (0.45 + 0.55 * shelter);
    return { v: s, u: Math.cos(a), w: Math.sin(a) };
  }
  if (key === "waves") {
    // tuned so a normal day sits in Calm/Moderate and only patches go Rough —
    // a map that is mostly red teaches people to ignore it
    const swell = 0.20 + 3.0 * clamp01((f.m - 0.35) / 1.0);
    const h = (0.25 + swell) * (0.35 + 0.65 * shelter);
    const a = Math.atan2(f.dirV, f.dirU) * 0.35 + 0.72; // swell mostly from SW
    return { v: h, u: Math.cos(a), w: Math.sin(a), p: 5 + 3 * shelter };
  }
  if (key === "sst") {
    const n2 = noise((lon - 72.7) * 2.1, (lat - 18.95) * 2.1, t * 0.5);
    return { v: 28.4 + 2.1 * n2 - 0.9 * shelter, u: 0, w: 0 };
  }
  // chlorophyll: coastal bloom decaying offshore, with patchiness
  const n3 = noise((lon - 72.7) * 4.6, (lat - 18.95) * 4.6, t * 0.35);
  const base = 9.5 * Math.exp(-Math.max(0, off) / 14) + 0.12;
  return { v: Math.max(0.03, base * (0.55 + 0.85 * (n3 * 0.5 + 0.5))), u: 0, w: 0 };
}

// ------------------------------------------------------------ live data
export const GRID = { lon0: 72.2, lat0: 18.3, lon1: 73.3, lat1: 19.7, nx: 11, ny: 12 } as const;
const G_DLON = (GRID.lon1 - GRID.lon0) / (GRID.nx - 1);
const G_DLAT = (GRID.lat1 - GRID.lat0) / (GRID.ny - 1);

type Series = (number | null)[];

interface LiveCell {
  wave: Series; waveDir: Series; period: Series; sst: Series;
  curV: Series; curDir: Series; windV: Series; windDir: Series;
}

export interface LiveData {
  hours: string[];
  cells: LiveCell[];
  issued: Date;
  /** index into `hours` closest to the moment the data was loaded */
  nowIdx: number;
}

interface OpenMeteoLocation {
  hourly: { time: string[] } & Record<string, Series | string[]>;
}

let live: LiveData | null = null;
export const getLive = (): LiveData | null => live;

function gridPoints(): [number, number][] {
  const pts: [number, number][] = [];
  for (let j = 0; j < GRID.ny; j++)
    for (let i = 0; i < GRID.nx; i++)
      pts.push([+(GRID.lat0 + j * G_DLAT).toFixed(4), +(GRID.lon0 + i * G_DLON).toFixed(4)]);
  return pts;
}

function nearestHourIndex(hours: string[]): number {
  const now = Date.now();
  let best = 0, bestD = Infinity;
  hours.forEach((h, i) => {
    const d = Math.abs(new Date(h).getTime() - now);
    if (d < bestD) { bestD = d; best = i; }
  });
  return best;
}

export async function loadLiveData(signal?: AbortSignal): Promise<LiveData | null> {
  const pts = gridPoints();
  const lats = pts.map((p) => p[0]).join(",");
  const lons = pts.map((p) => p[1]).join(",");
  const marineUrl = `https://marine-api.open-meteo.com/v1/marine?latitude=${lats}&longitude=${lons}`
    + "&hourly=wave_height,wave_direction,wave_period,sea_surface_temperature,ocean_current_velocity,ocean_current_direction"
    + "&forecast_days=3&timezone=auto";
  const windUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lats}&longitude=${lons}`
    + "&hourly=wind_speed_10m,wind_direction_10m&wind_speed_unit=ms&forecast_days=3&timezone=auto";
  try {
    const [mRes, wRes] = await Promise.all([fetch(marineUrl, { signal }), fetch(windUrl, { signal })]);
    if (!mRes.ok || !wRes.ok) return null;
    const m = (await mRes.json()) as OpenMeteoLocation | OpenMeteoLocation[];
    const w = (await wRes.json()) as OpenMeteoLocation | OpenMeteoLocation[];
    const ma = Array.isArray(m) ? m : [m];
    const wa = Array.isArray(w) ? w : [w];
    if (ma.length !== pts.length || wa.length !== pts.length) return null;

    const hours = ma[0].hourly.time;
    const cells: LiveCell[] = ma.map((loc, i) => ({
      wave: loc.hourly.wave_height as Series,
      waveDir: loc.hourly.wave_direction as Series,
      period: loc.hourly.wave_period as Series,
      sst: loc.hourly.sea_surface_temperature as Series,
      curV: loc.hourly.ocean_current_velocity as Series, // km/h
      curDir: loc.hourly.ocean_current_direction as Series,
      windV: wa[i].hourly.wind_speed_10m as Series, // m/s
      windDir: wa[i].hourly.wind_direction_10m as Series,
    }));
    live = { hours, cells, issued: new Date(), nowIdx: nearestHourIndex(hours) };
    return live;
  } catch {
    return null;
  }
}

function cellVal(arr: Series | undefined, h: number): number {
  const v = arr?.[h];
  return v === null || v === undefined ? NaN : v;
}

/** Bilinear over the grid. Directions are interpolated as vectors, never as
 *  angles — averaging 350° and 10° as numbers gives you 180°, i.e. backwards. */
function sampleLive(data: LiveData, key: FieldKey, lon: number, lat: number, hour: number): Sample | null {
  const fx = (lon - GRID.lon0) / G_DLON, fy = (lat - GRID.lat0) / G_DLAT;
  const i0 = Math.max(0, Math.min(GRID.nx - 2, Math.floor(fx)));
  const j0 = Math.max(0, Math.min(GRID.ny - 2, Math.floor(fy)));
  const tx = clamp01(fx - i0), ty = clamp01(fy - j0);
  const corners: [number, number, number][] = [
    [i0, j0, (1 - tx) * (1 - ty)], [i0 + 1, j0, tx * (1 - ty)],
    [i0, j0 + 1, (1 - tx) * ty], [i0 + 1, j0 + 1, tx * ty],
  ];

  let val = 0, wsum = 0, u = 0, w = 0, per = 0, pw = 0;
  for (const [i, j, wt] of corners) {
    const c = data.cells[j * GRID.nx + i];
    if (!c) continue;
    let v: number, dirDeg = NaN, toward = false;
    if (key === "waves") {
      v = cellVal(c.wave, hour); dirDeg = cellVal(c.waveDir, hour);
      const T = cellVal(c.period, hour);
      if (isFinite(T)) { per += T * wt; pw += wt; }
    } else if (key === "wind") {
      v = cellVal(c.windV, hour); dirDeg = cellVal(c.windDir, hour);
    } else if (key === "currents") {
      v = cellVal(c.curV, hour) / 3.6; dirDeg = cellVal(c.curDir, hour); toward = true;
    } else if (key === "sst") {
      v = cellVal(c.sst, hour);
    } else {
      return null;
    }
    if (!isFinite(v)) continue;
    val += v * wt; wsum += wt;
    if (isFinite(dirDeg)) {
      const d = ((toward ? dirDeg : dirDeg + 180) * Math.PI) / 180; // -> direction of travel
      u += Math.sin(d) * v * wt; w += Math.cos(d) * v * wt;
    }
  }
  if (!wsum) return null;
  const mag = Math.hypot(u, w) || 1;
  const out: Sample = { v: val / wsum, u: u / mag, w: w / mag };
  if (pw) out.p = per / pw; // real wave period, seconds
  return out;
}

/**
 * Read a field. `t` drives the synthetic model; `hour` indexes the live
 * forecast. Chlorophyll has no free live source, so it always stays
 * modelled — and the UI says so rather than dressing it up as observed.
 */
export function sampleField(key: FieldKey, lon: number, lat: number, t: number, hour: number): Sample {
  if (live && key !== "chl") {
    const s = sampleLive(live, key, lon, lat, hour);
    if (s) return s;
  }
  return sampleSynthetic(key, lon, lat, t);
}
