import type L from "leaflet";
import indiaLand from "@/public/data/india-land.json";
import { COAST_ISLANDS, COAST_MAIN } from "./coast";
import { sampleField } from "./field";
import { BANDS, VECTOR_FIELDS, bandOf, formatValue, hexRgb, normValue, rampLUT } from "./ramps";
import type { FieldKey } from "./types";

export interface RenderConfig {
  overlay: FieldKey;
  simple: boolean;
  particles: boolean;
  values: boolean;
  t: number;
  hour: number;
}

interface View {
  w: number;
  h: number;
  lon0: number;
  lat0: number;
  dLon: number;
  dLat: number;
}

interface Particle {
  x: number;
  y: number;
  age: number;
}

const MASK_STEP = 4; // land-mask resolution divisor
const RSTEP = 6; // field sampled every N css px
const MAXAGE = 92;

/**
 * Two canvases in a Leaflet pane: a smooth raster of the active field and
 * streamline trails advected through it. Redrawn from scratch on every
 * settle (moveend/zoomend) and hidden while the map is moving.
 */
export class FieldRenderer {
  cfg: RenderConfig;
  private map: L.Map;
  private raster = document.createElement("canvas");
  private fx = document.createElement("canvas");
  private rctx: CanvasRenderingContext2D;
  private fctx: CanvasRenderingContext2D;
  private mask: Uint8ClampedArray | null = null;
  private mw = 0;
  private mh = 0;
  private view: View | null = null;
  private parts: Particle[] = [];
  private anim = 0;

  constructor(map: L.Map, pane: HTMLElement, cfg: RenderConfig) {
    this.map = map;
    this.cfg = cfg;
    for (const c of [this.raster, this.fx]) {
      c.style.position = "absolute";
      c.style.left = "0";
      c.style.top = "0";
      pane.appendChild(c);
    }
    this.rctx = this.raster.getContext("2d")!;
    this.fctx = this.fx.getContext("2d")!;
  }

  // ------------------------------------------------------------ land
  private landPath(ctx: CanvasRenderingContext2D, scale: number) {
    const pt = (la: number, lo: number): [number, number] => {
      const p = this.map.latLngToContainerPoint([la, lo]);
      return [p.x / scale, p.y / scale];
    };

    const b = this.map.getBounds();
    const minLat = b.getSouth() - 1, maxLat = b.getNorth() + 1;
    const minLon = b.getWest() - 1, maxLon = b.getEast() + 1;

    ctx.beginPath();
    const polygons = (indiaLand as unknown as { polygons: [number, number][][][] }).polygons;
    for (let i = 0; i < polygons.length; i++) {
      const rings = polygons[i];
      if (!rings.length || !rings[0].length) continue;

      // Quick bounding box check on exterior ring
      const ext = rings[0];
      let pMinLat = ext[0][0], pMaxLat = ext[0][0], pMinLon = ext[0][1], pMaxLon = ext[0][1];
      for (let k = 1; k < ext.length; k++) {
        const la = ext[k][0], lo = ext[k][1];
        if (la < pMinLat) pMinLat = la;
        if (la > pMaxLat) pMaxLat = la;
        if (lo < pMinLon) pMinLon = lo;
        if (lo > pMaxLon) pMaxLon = lo;
      }
      if (pMinLat > maxLat || pMaxLat < minLat || pMinLon > maxLon || pMaxLon < minLon) {
        continue;
      }

      for (let r = 0; r < rings.length; r++) {
        const ring = rings[r];
        if (!ring.length) continue;
        const [x0, y0] = pt(ring[0][0], ring[0][1]);
        ctx.moveTo(x0, y0);
        for (let j = 1; j < ring.length; j++) {
          const [x, y] = pt(ring[j][0], ring[j][1]);
          ctx.lineTo(x, y);
        }
        ctx.closePath();
      }
    }
  }

  private buildMask(w: number, h: number) {
    this.mw = Math.ceil(w / MASK_STEP);
    this.mh = Math.ceil(h / MASK_STEP);
    const c = document.createElement("canvas");
    c.width = this.mw;
    c.height = this.mh;
    const g = c.getContext("2d", { willReadFrequently: true })!;
    g.fillStyle = "#fff";
    this.landPath(g, MASK_STEP);
    g.fill("evenodd");
    this.mask = g.getImageData(0, 0, this.mw, this.mh).data;
  }

  isLand(px: number, py: number): boolean {
    if (!this.mask) return false;
    const mx = (px / MASK_STEP) | 0, my = (py / MASK_STEP) | 0;
    if (mx < 0 || my < 0 || mx >= this.mw || my >= this.mh) return false;
    return this.mask[(my * this.mw + mx) * 4 + 3] > 110;
  }

  // ------------------------------------------------------------ view
  sync() {
    if (!this.map) return;
    try {
      const pane = (this.map as unknown as { _mapPane?: { _leaflet_pos?: unknown } })._mapPane;
      if (!pane || !pane._leaflet_pos) return;
      const size = this.map.getSize();
      if (!size || !size.x || !size.y) return;
      const b = this.map.getBounds();
      if (!b || !b.isValid()) return;
      const w = size.x, h = size.y;
      if (!w || !h) return;
      this.view = {
        w, h,
        lon0: b.getWest(), lat0: b.getNorth(),
        dLon: (b.getEast() - b.getWest()) / w,
        dLat: (b.getSouth() - b.getNorth()) / h,
      };
      const tl = this.map.containerPointToLayerPoint([0, 0]);
      for (const c of [this.raster, this.fx]) c.style.transform = `translate3d(${tl.x}px,${tl.y}px,0)`;
      this.fx.width = w;
      this.fx.height = h;
      this.fx.style.width = `${w}px`;
      this.fx.style.height = `${h}px`;
      this.buildMask(w, h);
      this.drawRaster();
      this.resetParticles();
    } catch {
      // Leaflet map pane layout still initializing; will sync safely on next event
    }
  }

  // ---------------------------------------------------------- raster
  drawRaster() {
    const view = this.view;
    if (!view) return;
    const { w, h } = view;
    const { overlay: key, t, hour, simple } = this.cfg;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    this.raster.width = w * dpr;
    this.raster.height = h * dpr;
    this.raster.style.width = `${w}px`;
    this.raster.style.height = `${h}px`;
    const rctx = this.rctx;
    rctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    rctx.clearRect(0, 0, w, h);

    const gw = Math.ceil(w / RSTEP), gh = Math.ceil(h / RSTEP);
    const off = document.createElement("canvas");
    off.width = gw;
    off.height = gh;
    const octx = off.getContext("2d")!;
    const img = octx.createImageData(gw, gh);
    const lut = rampLUT(key);
    const bandRGB = BANDS[key].steps.map((s) => hexRgb(s.color));

    for (let gy = 0; gy < gh; gy++) {
      const py = gy * RSTEP, lat = view.lat0 + py * view.dLat;
      for (let gx = 0; gx < gw; gx++) {
        const px = gx * RSTEP;
        const o = (gy * gw + gx) * 4;
        if (this.isLand(px, py)) { img.data[o + 3] = 0; continue; }
        const s = sampleField(key, view.lon0 + px * view.dLon, lat, t, hour);
        if (simple) {
          const c = bandRGB[bandOf(key, s.v).i];
          img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2];
          img.data[o + 3] = 168;
        } else {
          const i = Math.round(normValue(key, s.v) * 255) * 3;
          img.data[o] = lut[i]; img.data[o + 1] = lut[i + 1]; img.data[o + 2] = lut[i + 2];
          img.data[o + 3] = 218;
        }
      }
    }
    octx.putImageData(img, 0, 0);
    rctx.imageSmoothingEnabled = true;
    rctx.imageSmoothingQuality = "high";
    rctx.drawImage(off, 0, 0, gw, gh, 0, 0, gw * RSTEP, gh * RSTEP);

    // feather the coast so the field doesn't end on a hard pixel edge
    rctx.save();
    rctx.globalCompositeOperation = "destination-out";
    rctx.lineWidth = 2.5;
    rctx.strokeStyle = "rgba(0,0,0,.55)";
    this.landPath(rctx, 1);
    rctx.fill("evenodd");
    rctx.stroke();
    rctx.restore();

    if (this.cfg.values) this.drawValueLabels();
  }

  private drawValueLabels() {
    const view = this.view!;
    const { w, h } = view;
    const { overlay: key, t, hour } = this.cfg;
    const step = 132;
    const rctx = this.rctx;
    rctx.font = '600 11px "IBM Plex Mono", ui-monospace, monospace';
    rctx.textAlign = "center";
    rctx.textBaseline = "middle";
    rctx.lineJoin = "round";
    for (let py = step * 0.6; py < h - 14; py += step) {
      for (let px = Math.round(py / step) % 2 ? step * 0.9 : step * 0.35; px < w - 18; px += step) {
        if (this.isLand(px, py)) continue;
        const s = sampleField(key, view.lon0 + px * view.dLon, view.lat0 + py * view.dLat, t, hour);
        const txt = formatValue(key, s.v);
        rctx.strokeStyle = "rgba(255,255,255,.85)";
        rctx.lineWidth = 3;
        rctx.strokeText(txt, px, py);
        rctx.fillStyle = "rgba(18,49,59,.86)";
        rctx.fillText(txt, px, py);
      }
    }
  }

  // ----------------------------------------------------- streamlines
  resetParticles() {
    const view = this.view;
    if (!view) return;
    const n = Math.max(260, Math.min(2400, Math.round((view.w * view.h) / (this.cfg.simple ? 980 : 520))));
    this.parts = Array.from({ length: n }, () => this.spawn({ x: 0, y: 0, age: 0 }, true));
  }

  clearTrails() {
    this.fctx.clearRect(0, 0, this.fx.width, this.fx.height);
  }

  private spawn(p: Particle, rndAge: boolean): Particle {
    const view = this.view!;
    let x: number, y: number, tries = 0;
    do {
      x = Math.random() * view.w;
      y = Math.random() * view.h;
      tries++;
    } while (this.isLand(x, y) && tries < 12);
    p.x = x;
    p.y = y;
    p.age = rndAge ? Math.random() * MAXAGE : 0;
    return p;
  }

  private step() {
    const view = this.view;
    if (!view || !this.cfg.particles) return;
    const { w, h } = view;
    const fctx = this.fctx;
    fctx.globalCompositeOperation = "destination-in";
    fctx.fillStyle = "rgba(0,0,0,0.945)"; // longer trails
    fctx.fillRect(0, 0, w, h);
    fctx.globalCompositeOperation = "source-over";

    const { overlay, t, hour, simple } = this.cfg;
    if (!VECTOR_FIELDS.has(overlay)) return;
    const key = overlay;
    /* Wind and current streaks move at the speed of the thing itself. Swell
       doesn't work like that — the water barely moves, the *form* travels, at
       roughly c = 1.56·T in deep water. So waves are advected by the real wave
       period, not by wave height (which only sets the colour). */
    const gain = key === "wind" ? 0.30 : key === "currents" ? 3.6 : 0.075;
    const pxLon = 1 / view.dLon, pxLat = 1 / view.dLat;
    const buckets: number[][] = [[], [], []];

    for (const p of this.parts) {
      const s = sampleField(key, view.lon0 + p.x * view.dLon, view.lat0 + p.y * view.dLat, t, hour);
      const celerity = key === "waves" && s.p ? 1.56 * s.p : null; // m/s, deep water
      const spd = (celerity ?? s.v) * gain;
      const nx = p.x + s.u * spd * pxLon * 0.0009;
      const ny = p.y - s.w * spd * pxLat * 0.0009;
      if (p.age++ > MAXAGE || nx < 0 || ny < 0 || nx > w || ny > h || this.isLand(nx, ny)) {
        this.spawn(p, false);
        continue;
      }
      const tier = normValue(key, s.v);
      buckets[tier > 0.62 ? 2 : tier > 0.32 ? 1 : 0].push(p.x, p.y, nx, ny);
      p.x = nx;
      p.y = ny;
    }

    // On pale water an ink streak reads better than a white one; a soft white
    // halo underneath keeps it legible again once the field turns saturated.
    const inks = simple ? [0.20, 0.27, 0.36] : [0.34, 0.46, 0.60];
    const widths = [1.0, 1.15, 1.35];
    fctx.lineCap = "round";
    for (let b = 0; b < 3; b++) {
      const arr = buckets[b];
      if (!arr.length) continue;
      fctx.beginPath();
      for (let i = 0; i < arr.length; i += 4) {
        fctx.moveTo(arr[i], arr[i + 1]);
        fctx.lineTo(arr[i + 2], arr[i + 3]);
      }
      fctx.strokeStyle = simple ? "rgba(255,255,255,.38)" : "rgba(255,255,255,.55)";
      fctx.lineWidth = widths[b] + 1.6;
      fctx.stroke();
      fctx.strokeStyle = `rgba(16,46,58,${inks[b]})`;
      fctx.lineWidth = widths[b];
      fctx.stroke();
    }
  }

  private loop = () => {
    this.step();
    this.anim = requestAnimationFrame(this.loop);
  };

  start() {
    if (!this.anim) this.anim = requestAnimationFrame(this.loop);
  }

  stop() {
    if (this.anim) cancelAnimationFrame(this.anim);
    this.anim = 0;
  }

  destroy() {
    this.stop();
    this.raster.remove();
    this.fx.remove();
  }
}
