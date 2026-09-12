'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';

interface WeatherLayerProps {
  data: GeoJSON.FeatureCollection;
  visible?: boolean;
}

export const WeatherLayer: React.FC<WeatherLayerProps> = ({ data, visible = false }) => {
  const { map, isLoaded } = useMarineMap();
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!map || !isLoaded) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    data.features.forEach((feature) => {
      if (feature.geometry.type === 'Point') {
        const coords = feature.geometry.coordinates as [number, number];
        const props = feature.properties || {};

        const speed = Number(props.wind_speed_knots) || 10;
        const deg = Number(props.wind_direction_deg) || 0;
        const wave = Number(props.wave_height_m) || 1.0;
        const isHazard = speed >= 20 || wave >= 2.0;
        const isCaution = speed >= 14 && speed < 20;

        const arrowColor = isHazard ? '#ef4444' : isCaution ? '#f59e0b' : '#38bdf8';
        const bgColor = isHazard ? 'rgba(239, 68, 68, 0.2)' : isCaution ? 'rgba(245, 158, 11, 0.2)' : 'rgba(56, 189, 248, 0.2)';

        // Container
        const el = document.createElement('div');
        el.className = 'weather-vector-container';
        el.style.display = visible ? 'flex' : 'none';
        el.style.flexDirection = 'column';
        el.style.alignItems = 'center';
        el.style.cursor = 'pointer';
        el.style.userSelect = 'none';

        // Wind Arrow Icon rotated to wind degree
        const arrowBox = document.createElement('div');
        arrowBox.style.width = '24px';
        arrowBox.style.height = '24px';
        arrowBox.style.borderRadius = '50%';
        arrowBox.style.backgroundColor = bgColor;
        arrowBox.style.border = `1.5px solid ${arrowColor}`;
        arrowBox.style.display = 'flex';
        arrowBox.style.alignItems = 'center';
        arrowBox.style.justifyContent = 'center';
        arrowBox.style.transform = `rotate(${deg}deg)`;
        arrowBox.style.boxShadow = `0 0 10px ${arrowColor}`;

        // Arrow shape
        const arrow = document.createElement('div');
        arrow.style.width = '0';
        arrow.style.height = '0';
        arrow.style.borderLeft = '4px solid transparent';
        arrow.style.borderRight = '4px solid transparent';
        arrow.style.borderBottom = `9px solid ${arrowColor}`;
        arrowBox.appendChild(arrow);

        // Telemetry Pill Badge: Wind speed & Wave height
        const badge = document.createElement('div');
        badge.style.marginTop = '3px';
        badge.style.padding = '2px 5px';
        badge.style.borderRadius = '4px';
        badge.style.backgroundColor = 'rgba(6, 13, 26, 0.9)';
        badge.style.border = `1px solid ${arrowColor}`;
        badge.style.color = '#f8fafc';
        badge.style.fontSize = '9px';
        badge.style.fontWeight = '700';
        badge.style.whiteSpace = 'nowrap';
        badge.innerText = `${speed} kts • ${wave}m`;

        el.appendChild(arrowBox);
        el.appendChild(badge);

        const popup = new maplibregl.Popup({ offset: 16, closeButton: false }).setHTML(`
          <div style="font-family: inherit; font-size: 11px; padding: 6px 8px; color: #0a1324; max-width: 220px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
              <strong style="color: ${isHazard ? '#b91c1c' : '#0369a1'};">🌬️ ${props.name || 'Marine Weather Sector'}</strong>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin: 4px 0; font-size: 10px;">
              <div>Wind: <strong>${speed} kts (${props.wind_direction_cardinal || 'WSW'})</strong></div>
              <div>Wave ($H_s$): <strong>${wave} m</strong></div>
              <div>Swell: <strong>${props.swell_period_sec || 8.0}s</strong></div>
              <div>State: <strong>${props.sea_state || 'Normal'}</strong></div>
            </div>
            <div style="font-size: 9.5px; color: #475569; border-top: 1px solid #e2e8f0; padding-top: 4px; margin-top: 4px;">
              ${props.advisory || 'Normal coastal conditions'}
            </div>
            <div style="font-size: 8.5px; color: #94a3b8; margin-top: 2px;">
              Source: IMD Ocean Marine Forecast (Mock)
            </div>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat(coords)
          .setPopup(popup)
          .addTo(map);

        markersRef.current.push(marker);
      }
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
    };
  }, [map, isLoaded, data, visible]);

  return null;
};
