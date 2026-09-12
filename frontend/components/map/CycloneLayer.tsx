'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';

interface CycloneLayerProps {
  data: GeoJSON.FeatureCollection;
  visible?: boolean;
}

const LINE_SOURCE_ID = 'cyclone-track-source';
const LINE_LAYER_ID = 'cyclone-track-layer';
const BUFFER_SOURCE_ID = 'cyclone-buffer-source';
const BUFFER_FILL_ID = 'cyclone-buffer-fill';
const BUFFER_LINE_ID = 'cyclone-buffer-line';

export const CycloneLayer: React.FC<CycloneLayerProps> = ({ data, visible = false }) => {
  const { map, isLoaded } = useMarineMap();
  const eyeMarkerRef = useRef<maplibregl.Marker | null>(null);

  useEffect(() => {
    if (!map || !isLoaded) return;

    if (eyeMarkerRef.current) {
      eyeMarkerRef.current.remove();
      eyeMarkerRef.current = null;
    }

    const lineFeatures: GeoJSON.Feature[] = [];
    const polygonFeatures: GeoJSON.Feature[] = [];
    let eyeCoords: [number, number] | null = null;
    let eyeProps: any = null;

    data.features.forEach((f) => {
      if (f.geometry.type === 'Point') {
        eyeCoords = f.geometry.coordinates as [number, number];
        eyeProps = f.properties;
      } else if (f.geometry.type === 'LineString') {
        lineFeatures.push(f);
      } else if (f.geometry.type === 'Polygon') {
        polygonFeatures.push(f);
      }
    });

    // 1. Eye of the Storm DOM Marker
    if (eyeCoords && eyeProps) {
      const el = document.createElement('div');
      el.className = 'cyclone-eye-marker';
      el.style.display = visible ? 'flex' : 'none';
      el.style.flexDirection = 'column';
      el.style.alignItems = 'center';
      el.style.cursor = 'pointer';

      const pulse = document.createElement('div');
      pulse.style.width = '32px';
      pulse.style.height = '32px';
      pulse.style.borderRadius = '50%';
      pulse.style.backgroundColor = 'rgba(239, 68, 68, 0.35)';
      pulse.style.border = '2px solid #ef4444';
      pulse.style.display = 'flex';
      pulse.style.alignItems = 'center';
      pulse.style.justifyContent = 'center';
      pulse.style.fontSize = '16px';
      pulse.style.boxShadow = '0 0 16px rgba(239, 68, 68, 0.7)';
      pulse.innerText = '🌀';

      const tag = document.createElement('div');
      tag.style.marginTop = '2px';
      tag.style.padding = '2px 6px';
      tag.style.borderRadius = '4px';
      tag.style.backgroundColor = '#7f1d1d';
      tag.style.color = '#ffffff';
      tag.style.fontSize = '9px';
      tag.style.fontWeight = '800';
      tag.innerText = 'STORM EYE';

      el.appendChild(pulse);
      el.appendChild(tag);

      const popup = new maplibregl.Popup({ offset: 18, closeButton: false }).setHTML(`
        <div style="font-family: inherit; font-size: 11px; padding: 6px 8px; color: #0a1324; max-width: 240px;">
          <strong style="color: #b91c1c; font-size: 12px;">🌀 ${eyeProps.name}</strong><br/>
          <span style="font-size: 10px; color: #b91c1c; font-weight: 700;">${eyeProps.intensity}</span>
          <div style="margin: 6px 0; font-size: 10px; line-height: 1.4;">
            <div>Peak Wind Gusts: <strong>${eyeProps.wind_gusts_knots} kts</strong></div>
            <div>Central Pressure: <strong>${eyeProps.central_pressure_hpa} hPa</strong></div>
            <div>Movement: <strong>${eyeProps.movement_direction} at ${eyeProps.movement_speed_kmh} km/h</strong></div>
          </div>
          <div style="background: #fef2f2; border-left: 2px solid #ef4444; padding: 4px; font-size: 9.5px; color: #991b1b;">
            ${eyeProps.advisory}
          </div>
          <div style="font-size: 8.5px; color: #64748b; margin-top: 3px;">Authority: ${eyeProps.authority}</div>
        </div>
      `);

      eyeMarkerRef.current = new maplibregl.Marker({ element: el })
        .setLngLat(eyeCoords)
        .setPopup(popup)
        .addTo(map);
    }

    // 2. Trajectory Track and Hazard Buffer
    const safeAddCycloneVectors = () => {
      if (!map.isStyleLoaded()) {
        map.once('styledata', safeAddCycloneVectors);
        return;
      }

      // Buffer
      if (!map.getSource(BUFFER_SOURCE_ID)) {
        map.addSource(BUFFER_SOURCE_ID, {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: polygonFeatures },
        });

        map.addLayer({
          id: BUFFER_FILL_ID,
          type: 'fill',
          source: BUFFER_SOURCE_ID,
          paint: {
            'fill-color': '#f97316',
            'fill-opacity': 0.15,
          },
        });

        map.addLayer({
          id: BUFFER_LINE_ID,
          type: 'line',
          source: BUFFER_SOURCE_ID,
          paint: {
            'line-color': '#f97316',
            'line-width': 1.5,
            'line-dasharray': [2, 2],
          },
        });
      }

      // Track Line
      if (!map.getSource(LINE_SOURCE_ID)) {
        map.addSource(LINE_SOURCE_ID, {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: lineFeatures },
        });

        map.addLayer({
          id: LINE_LAYER_ID,
          type: 'line',
          source: LINE_SOURCE_ID,
          paint: {
            'line-color': '#ea580c',
            'line-width': 3,
            'line-dasharray': [4, 2],
            'line-opacity': 0.9,
          },
        });
      }

      const vis = visible ? 'visible' : 'none';
      if (map.getLayer(BUFFER_FILL_ID)) map.setLayoutProperty(BUFFER_FILL_ID, 'visibility', vis);
      if (map.getLayer(BUFFER_LINE_ID)) map.setLayoutProperty(BUFFER_LINE_ID, 'visibility', vis);
      if (map.getLayer(LINE_LAYER_ID)) map.setLayoutProperty(LINE_LAYER_ID, 'visibility', vis);
    };

    safeAddCycloneVectors();

    return () => {
      if (eyeMarkerRef.current) {
        eyeMarkerRef.current.remove();
        eyeMarkerRef.current = null;
      }
      if (map && map.getStyle()) {
        if (map.getLayer(LINE_LAYER_ID)) map.removeLayer(LINE_LAYER_ID);
        if (map.getLayer(BUFFER_LINE_ID)) map.removeLayer(BUFFER_LINE_ID);
        if (map.getLayer(BUFFER_FILL_ID)) map.removeLayer(BUFFER_FILL_ID);
        if (map.getSource(LINE_SOURCE_ID)) map.removeSource(LINE_SOURCE_ID);
        if (map.getSource(BUFFER_SOURCE_ID)) map.removeSource(BUFFER_SOURCE_ID);
      }
    };
  }, [map, isLoaded, data, visible]);

  return null;
};
