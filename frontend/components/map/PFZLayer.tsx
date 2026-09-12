'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';

interface PFZLayerProps {
  data: GeoJSON.FeatureCollection;
  visible?: boolean;
}

const SOURCE_ID = 'pfz-line-source';
const LINE_LAYER_ID = 'pfz-line-layer';

export const PFZLayer: React.FC<PFZLayerProps> = ({ data, visible = true }) => {
  const { map, isLoaded } = useMarineMap();
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!map || !isLoaded) return;

    // 1. Hotspot Markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    const lineFeatures: GeoJSON.Feature[] = [];

    data.features.forEach((feature) => {
      if (feature.geometry.type === 'Point') {
        const coords = feature.geometry.coordinates as [number, number];
        const props = feature.properties || {};

        const el = document.createElement('div');
        el.className = 'pfz-hotspot-marker';
        el.style.display = visible ? 'flex' : 'none';
        el.style.flexDirection = 'column';
        el.style.alignItems = 'center';
        el.style.cursor = 'pointer';

        const dot = document.createElement('div');
        dot.style.width = '10px';
        dot.style.height = '10px';
        dot.style.borderRadius = '50%';
        dot.style.backgroundColor = '#518bdb';
        dot.style.border = '2px solid #ffffff';
        dot.style.boxShadow = '0 2px 8px rgba(81, 139, 219, 0.4)';

        el.appendChild(dot);

        const confidencePct = Math.round((Number(props.confidence) || 0.85) * 100);
        const popup = new maplibregl.Popup({ offset: 12, closeButton: false }).setHTML(`
          <div style="font-family: inherit; font-size: 11px; padding: 4px 6px; color: #221f1c;">
            <strong style="color: #518bdb;">🐟 ${props.name || 'PFZ Hotspot'}</strong><br/>
            <span>Confidence: <strong>${confidencePct}%</strong></span><br/>
            <span>Front: <em>${props.sst_delta || 'Thermal Front'}</em></span><br/>
            <span style="font-size: 9px; color: #797267;">Source: ${props.source || 'INCOIS Mock'}</span>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      } else if (feature.geometry.type === 'LineString') {
        lineFeatures.push(feature);
      }
    });

    // 2. Safe Vector Line Layer for Convergence Front
    const safeAddLine = () => {
      if (!map.isStyleLoaded()) {
        map.once('styledata', safeAddLine);
        return;
      }

      const lineGeoJson: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: lineFeatures,
      };

      if (!map.getSource(SOURCE_ID)) {
        map.addSource(SOURCE_ID, {
          type: 'geojson',
          data: lineGeoJson,
        });

        map.addLayer({
          id: LINE_LAYER_ID,
          type: 'line',
          source: SOURCE_ID,
          paint: {
            'line-color': '#518bdb',
            'line-width': 2.5,
            'line-dasharray': [4, 2],
            'line-opacity': 0.85,
          },
        });
      } else {
        const src = map.getSource(SOURCE_ID) as maplibregl.GeoJSONSource;
        src.setData(lineGeoJson);
      }

      if (map.getLayer(LINE_LAYER_ID)) {
        map.setLayoutProperty(LINE_LAYER_ID, 'visibility', visible ? 'visible' : 'none');
      }
    };

    safeAddLine();

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
      if (map && map.getStyle()) {
        if (map.getLayer(LINE_LAYER_ID)) map.removeLayer(LINE_LAYER_ID);
        if (map.getSource(SOURCE_ID)) map.removeSource(SOURCE_ID);
      }
    };
  }, [map, isLoaded, data, visible]);

  return null;
};
