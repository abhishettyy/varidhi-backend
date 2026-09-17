"use client";

import type { FeatureCollection } from "geojson";
import L from "leaflet";
import { useEffect, useRef, type RefObject } from "react";
import type { MapApi, SpotEvent } from "@/components/console/types";
import {
  CYCLONE, GROUNDS, Ground, MAP_BOUNDS, MAP_CENTER, RESTRICTED, RESTRICTED_LABEL, RISK_ZONES, VESSELS, tierColor,
} from "@/lib/marine/data";
import { haversineKm, sampleField } from "@/lib/marine/field";
import { FieldRenderer, type RenderConfig } from "@/lib/marine/renderer";
import type { FieldKey, LatLon, MarkerKey } from "@/lib/marine/types";
import { setProbe } from "@/lib/probe-store";
import { FishingZone } from "@/types/marine";

export interface MarineMapProps {
  overlay: FieldKey;
  simple: boolean;
  particles: boolean;
  values: boolean;
  t: number;
  hour: number;
  dataVersion: number;
  markers: Record<MarkerKey, boolean>;
  home: LatLon;
  features?: FeatureCollection | null;
  backendZones?: FishingZone[];
  selectedZoneId?: string | null;
  apiRef?: RefObject<MapApi | null>;
  onHomeChange: (ll: LatLon) => void;
  onSpot: (spot: SpotEvent | null) => void;
  onSelectZone?: (zone: FishingZone) => void;
}

const BASE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}";
const LABEL_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}";

const boatIcon = () => L.divIcon({
  className: "",
  iconSize: [22, 22],
  iconAnchor: [11, 11],
  html: `<div class="boat"><div class="boat-pulse"></div>
    <svg width="22" height="22" viewBox="0 0 22 22"><circle cx="11" cy="11" r="6.5" fill="#087EA4" stroke="#fff" stroke-width="2.5"/></svg></div>`,
});

const textEl = (text: string) => {
  const s = document.createElement("span");
  s.textContent = text;
  return s;
};

function buildGroundsFromZones(
  zones: FishingZone[],
  simple: boolean,
  home: LatLon,
  selectedZoneId?: string | null,
  onSelectZone?: (zone: FishingZone) => void
): L.LayerGroup {
  const WORD = ["Recommended", "Alternative", "Caution"];
  return L.layerGroup(zones.map((z, i) => {
    const isSelected = selectedZoneId === z.id;
    const col = z.status === 'recommended' ? '#3FAF8F' : z.status === 'restricted' ? '#D6334C' : '#E8A93C';
    const score = Math.round((z.opportunity_score || 0) * (z.opportunity_score <= 1 ? 100 : 1));
    const [zLon, zLat] = z.coordinates;
    const km = z.distance_km ?? Math.round(haversineKm(home.lat, home.lon, zLat, zLon));
    const chip = simple ? `${WORD[i] ?? z.status.toUpperCase()} · ${km} km` : `${score}% · ${km} km`;
    
    const marker = L.marker([zLat, zLon], {
      icon: L.divIcon({
        className: "pfz-pin",
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        html: `<div style="position:relative; transform: ${isSelected ? 'scale(1.15)' : 'scale(1)'}; transition: transform 0.2s ease">
          <div class="pfz-dot" style="border: ${isSelected ? '3.5px solid #087EA4' : `2.5px solid ${col}`}; box-shadow: ${isSelected ? '0 0 0 4px rgba(8,126,164,0.3)' : '0 2px 7px rgba(18, 49, 59, 0.28)'}">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M3 12s3.5-5 8.5-5 8.5 5 8.5 5-3.5 5-8.5 5S3 12 3 12Z" stroke="${col}" stroke-width="2.2" stroke-linejoin="round"/>
              <circle cx="9.5" cy="12" r="1.5" fill="${col}"/></svg>
          </div>
          <div class="ground-chip" style="color: ${col}; ${isSelected ? 'font-weight: 700; border: 1.5px solid #087EA4' : ''}">${chip}</div>
        </div>`,
      }),
    });

    marker.bindPopup(`
      <div style="font-family: inherit; min-width: 170px;">
        <div style="font-weight: 700; font-size: 13px; color: #12313b; margin-bottom: 2px;">${z.name}</div>
        <div style="font-size: 11px; color: ${col}; font-weight: 600; text-transform: uppercase; margin-bottom: 6px;">
          ${z.status} · Score: ${score}%
        </div>
        <div style="font-size: 11.5px; color: #607d86; line-height: 1.4;">
          Species: <b>${z.species?.slice(0, 2).join(', ') || 'Pelagic fish'}</b><br/>
          Depth: <b>${z.target_depth_m || 30}m</b><br/>
          Distance: <b>${km} km</b> from home
        </div>
      </div>
    `);

    if (onSelectZone) {
      marker.on('click', () => onSelectZone(z));
    }

    return marker;
  }));
}

function buildGroundsFallback(simple: boolean, home: LatLon): L.LayerGroup {
  const ranked = [...GROUNDS].sort((a, b) => b.score - a.score);
  const list = simple ? ranked.slice(0, 3) : ranked;
  const WORD = ["Best spot", "Good spot", "Worth a try"];
  return L.layerGroup(list.map((g, i) => {
    const col = tierColor(g.score);
    const km = Math.round(haversineKm(home.lat, home.lon, g.lat, g.lon));
    const chip = simple ? `${WORD[i] ?? "Option"} · ${km} km` : `${g.score}% · ${km} km`;
    return L.marker([g.lat, g.lon], {
      icon: L.divIcon({
        className: "pfz-pin", iconSize: [30, 30], iconAnchor: [15, 15],
        html: `<div style="position:relative">
          <div class="pfz-dot" style="border:2.5px solid ${col}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
              <path d="M3 12s3.5-5 8.5-5 8.5 5 8.5 5-3.5 5-8.5 5S3 12 3 12Z" stroke="${col}" stroke-width="1.9" stroke-linejoin="round"/>
              <circle cx="9.5" cy="12" r="1.2" fill="${col}"/></svg>
          </div>
          <div class="ground-chip" style="color:${col}">${chip}</div></div>`,
      }),
    }).bindPopup(`<b>${simple ? (WORD[i] ?? "Fishing ground") : `Ground ${g.id}`}</b><br>${g.species}<br>${km} km from you`);
  }));
}

function buildStaticLayers(): Partial<Record<MarkerKey, L.Layer>> {
  return {
    restricted: L.layerGroup([
      L.polygon(RESTRICTED, { color: "#D6334C", weight: 1.8, fillColor: "#D6334C", fillOpacity: 0.16, dashArray: "6,4" })
        .bindTooltip(RESTRICTED_LABEL, { sticky: true }),
    ]),
    risk: L.layerGroup(RISK_ZONES.map((z) =>
      L.polygon(z.ring, { color: z.color, weight: 1.5, fillColor: z.color, fillOpacity: 0.14, dashArray: "3,5" })
        .bindTooltip(`${z.level === "HIGH" ? "High" : "Moderate"} risk area`, { sticky: true }))),
    vessels: L.layerGroup(VESSELS.map(([la, lo, hd]) => L.marker([la, lo], {
      icon: L.divIcon({
        className: "", iconSize: [14, 14], iconAnchor: [7, 7],
        html: `<svg width="14" height="14" viewBox="0 0 14 14" style="transform:rotate(${hd}deg)">
          <path d="M7 1.5 11 12 7 9.6 3 12Z" fill="#607D86" stroke="#fff" stroke-width="1"/></svg>`,
      }),
    }))),
    cyclone: L.layerGroup([
      L.circle([CYCLONE.lat, CYCLONE.lon], { radius: CYCLONE.radiusM, color: "#E8A93C", weight: 1.6, dashArray: "7,5", fillColor: "#E8A93C", fillOpacity: 0.08 }),
      L.polyline(CYCLONE.track, { color: "#E8A93C", weight: 2, dashArray: "3,6" }),
      L.marker([CYCLONE.lat, CYCLONE.lon], {
        icon: L.divIcon({
          className: "", iconSize: [26, 26], iconAnchor: [13, 13],
          html: `<svg width="26" height="26" viewBox="0 0 26 26" fill="none">
            <path d="M13 13c0-4 3-6 6-5.5S24 12 20 14M13 13c0 4-3 6-6 5.5S2 14 6 12" stroke="#E8A93C" stroke-width="2.2" stroke-linecap="round"/>
            <circle cx="13" cy="13" r="2.2" fill="#E8A93C"/></svg>`,
        }),
      }).bindTooltip(CYCLONE.label, { sticky: true }),
    ]),
  };
}

export default function MarineMapLeaflet(props: MarineMapProps) {
  const {
    overlay, simple, particles, values, t, hour, dataVersion, markers, home, features,
    backendZones, selectedZoneId, onSelectZone
  } = props;
  const { lat: homeLat, lon: homeLon } = home;
  const elRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const rendererRef = useRef<FieldRenderer | null>(null);
  const layersRef = useRef<Partial<Record<MarkerKey, L.Layer>>>({});
  const boatRef = useRef<L.Marker | null>(null);
  const featureLayerRef = useRef<L.GeoJSON | null>(null);
  const prevModeRef = useRef({ overlay, simple });
  const propsRef = useRef(props);
  useEffect(() => {
    propsRef.current = props;
  });

  // ------------------------------------------------------------ mount
  useEffect(() => {
    const el = elRef.current!;
    const p = propsRef.current;
    /* Fit the whole operating area — port, zones, cyclone track — instead of
       dropping a fixed zoom on the boat, which left the map part-covered. */
    const map = L.map(el, {
      zoomControl: false,
      attributionControl: true,
      minZoom: 7,
      maxZoom: 14,
    }).fitBounds(MAP_BOUNDS, { padding: [26, 26] });
    mapRef.current = map;

    L.tileLayer(BASE_URL, { maxZoom: 16, attribution: "Esri, GEBCO, Garmin &copy; OpenStreetMap" }).addTo(map);
    const fieldPane = map.createPane("fieldPane");
    fieldPane.style.zIndex = "350";
    fieldPane.style.pointerEvents = "none";
    fieldPane.classList.add("orca-field-pane");
    const labelPane = map.createPane("labelPane");
    labelPane.style.zIndex = "460";
    labelPane.style.pointerEvents = "none";
    L.tileLayer(LABEL_URL, { maxZoom: 16, pane: "labelPane" }).addTo(map);
    L.control.scale({ position: "bottomleft", imperial: false, maxWidth: 110 }).addTo(map);

    const cfg: RenderConfig = {
      overlay: p.overlay, simple: p.simple, particles: p.particles, values: p.values, t: p.t, hour: p.hour,
    };
    const renderer = new FieldRenderer(map, fieldPane, cfg);
    rendererRef.current = renderer;

    layersRef.current = buildStaticLayers();

    const boat = L.marker([p.home.lat, p.home.lon], {
      icon: boatIcon(), draggable: true, zIndexOffset: 800, title: "Your position — drag to move",
    }).addTo(map);
    boat.on("dragend", () => {
      const ll = boat.getLatLng();
      propsRef.current.onHomeChange({ lat: ll.lat, lon: ll.lng });
    });
    boatRef.current = boat;

    map.on("movestart zoomstart", () => {
      fieldPane.style.opacity = "0";
      renderer.stop();
      propsRef.current.onSpot(null);
    });
    map.on("moveend zoomend resize", () => {
      renderer.sync();
      fieldPane.style.opacity = "1";
      renderer.start();
    });
    map.on("click", (e: L.LeafletMouseEvent) => {
      const pt = map.latLngToContainerPoint(e.latlng);
      const size = map.getSize();
      propsRef.current.onSpot({ lat: e.latlng.lat, lon: e.latlng.lng, x: pt.x, y: pt.y, w: size.x, h: size.y });
    });
    map.on("mousemove", (e: L.LeafletMouseEvent) => {
      const c = renderer.cfg;
      setProbe({
        lat: e.latlng.lat, lon: e.latlng.lng, key: c.overlay,
        sample: sampleField(c.overlay, e.latlng.lng, e.latlng.lat, c.t, c.hour),
      });
    });
    map.on("mouseout", () => setProbe(null));

    const ro = new ResizeObserver(() => map.invalidateSize());
    ro.observe(el);

    if (p.apiRef) {
      p.apiRef.current = {
        zoomBy: (d) => map.setZoom(map.getZoom() + d),
        panTo: (ll, zoom) => (zoom ? map.flyTo([ll.lat, ll.lon], zoom, { duration: 0.7 }) : map.panTo([ll.lat, ll.lon])),
      };
    }

    map.whenReady(() => {
      map.invalidateSize({ pan: false });
      renderer.sync();
      renderer.start();
    });

    return () => {
      ro.disconnect();
      renderer.destroy();
      map.remove();
      mapRef.current = null;
      rendererRef.current = null;
      featureLayerRef.current = null;
      if (p.apiRef) p.apiRef.current = null;
      setProbe(null);
    };
  }, []);

  // ------------------------------------------------------- field config
  useEffect(() => {
    const r = rendererRef.current;
    if (!r) return;
    r.cfg = { overlay, simple, particles, values, t, hour };
    const prev = prevModeRef.current;
    if (prev.overlay !== overlay || prev.simple !== simple) {
      r.clearTrails();
      r.resetParticles();
    }
    prevModeRef.current = { overlay, simple };
    if (!particles) r.clearTrails();
    r.drawRaster();
  }, [overlay, simple, particles, values, t, hour, dataVersion]);

  // --------------------------------------------------------- grounds
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const old = layersRef.current.pfz;
    if (old) map.removeLayer(old);

    const layer = (backendZones && backendZones.length > 0)
      ? buildGroundsFromZones(backendZones, simple, { lat: homeLat, lon: homeLon }, selectedZoneId, onSelectZone)
      : buildGroundsFallback(simple, { lat: homeLat, lon: homeLon });

    layersRef.current.pfz = layer;
    if (propsRef.current.markers.pfz) layer.addTo(map);
  }, [backendZones, selectedZoneId, simple, homeLat, homeLon, onSelectZone]);

  // --------------------------------------------------- marker toggles
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    for (const [k, layer] of Object.entries(layersRef.current)) {
      if (!layer) continue;
      const on = markers[k as MarkerKey];
      if (on && !map.hasLayer(layer)) layer.addTo(map);
      if (!on && map.hasLayer(layer)) map.removeLayer(layer);
    }
  }, [markers]);

  // ------------------------------------------------------------- boat
  useEffect(() => {
    const boat = boatRef.current;
    if (!boat) return;
    const cur = boat.getLatLng();
    if (cur.lat !== homeLat || cur.lng !== homeLon) boat.setLatLng([homeLat, homeLon]);
  }, [homeLat, homeLon]);

  // ------------------------------------------- agent answer on the map
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    featureLayerRef.current?.remove();
    featureLayerRef.current = null;
    if (!features?.features || !features.features.length) return;
    let n = 0;
    const layer = L.geoJSON(features, {
      style: (f) => f?.properties?.kind === "route"
        ? { color: "#087EA4", weight: 3.5, dashArray: "8 6", opacity: 0.95 }
        : { color: "#FF7666", weight: 1.5, fillOpacity: 0.14 },
      pointToLayer: (f, ll) => {
        const hazard = f?.properties?.kind === "hazard";
        n += 1;
        return L.marker(ll, {
          zIndexOffset: 700,
          icon: L.divIcon({
            className: "", iconSize: [26, 26], iconAnchor: [13, 13],
            html: `<div class="agent-pin" style="${hazard ? "background:#E8A93C" : ""}">${hazard ? "!" : n}</div>`,
          }),
        });
      },
      onEachFeature: (f, lyr) => {
        const label = f?.properties?.label;
        if (label) lyr.bindTooltip(textEl(String(label)), { direction: "top", offset: [0, -12] });
      },
    }).addTo(map);
    featureLayerRef.current = layer;
    const b = layer.getBounds();
    if (b.isValid()) map.flyToBounds(b.pad(0.35), { maxZoom: 12, duration: 0.8 });
  }, [features]);

  return <div ref={elRef} className="absolute inset-0 z-0 bg-water" style={{ width: '100%', height: '100%' }} />;
}
