'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';

interface VesselLayerProps {
  data: GeoJSON.FeatureCollection;
  visible?: boolean;
}

export const VesselLayer: React.FC<VesselLayerProps> = ({ data, visible = false }) => {
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

        const isCoastGuard = props.type === 'coast_guard_patrol';
        const color = isCoastGuard ? '#518bdb' : '#e5a057';

        // Container
        const el = document.createElement('div');
        el.className = 'vessel-marker';
        el.style.display = visible ? 'flex' : 'none';
        el.style.flexDirection = 'column';
        el.style.alignItems = 'center';
        el.style.cursor = 'pointer';

        // Vessel Icon & Direction Pointer
        const iconBox = document.createElement('div');
        iconBox.style.width = '24px';
        iconBox.style.height = '24px';
        iconBox.style.borderRadius = '50%';
        iconBox.style.backgroundColor = isCoastGuard ? 'rgba(81, 139, 219, 0.15)' : 'rgba(229, 160, 87, 0.15)';
        iconBox.style.border = `1.5px solid ${color}`;
        iconBox.style.display = 'flex';
        iconBox.style.alignItems = 'center';
        iconBox.style.justifyContent = 'center';
        iconBox.style.fontSize = '12px';
        iconBox.style.transform = `rotate(${props.heading_deg || 0}deg)`;
        iconBox.style.boxShadow = `0 2px 8px rgba(0, 0, 0, 0.08)`;
        iconBox.innerText = isCoastGuard ? '🛡️' : '⛵';

        // Label
        const badge = document.createElement('div');
        badge.style.marginTop = '2px';
        badge.style.padding = '1px 6px';
        badge.style.borderRadius = '4px';
        badge.style.backgroundColor = '#ffffff';
        badge.style.border = `1px solid rgba(39, 39, 42, 0.09)`;
        badge.style.color = '#221f1c';
        badge.style.fontSize = '8.5px';
        badge.style.fontWeight = '600';
        badge.style.whiteSpace = 'nowrap';
        badge.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
        badge.innerText = `${props.name} • ${props.speed_knots} kts`;

        el.appendChild(iconBox);
        el.appendChild(badge);

        const popup = new maplibregl.Popup({ offset: 14, closeButton: false }).setHTML(`
          <div style="font-family: inherit; font-size: 11px; padding: 6px 8px; color: #221f1c; max-width: 220px;">
            <strong style="color: ${isCoastGuard ? '#518bdb' : '#221f1c'}; font-size: 12px;">
              ${isCoastGuard ? '🛡️ Coastal Patrol' : '⚓ Fishing Vessel'}
            </strong><br/>
            <strong>${props.name}</strong><br/>
            <span style="font-size: 10px; color: #797267;">ID: ${props.vessel_id}</span>
            <div style="margin-top: 4px; border-top: 1px solid rgba(39, 39, 42, 0.09); padding-top: 4px; font-size: 10px;">
              <div>Speed: <strong>${props.speed_knots} kts</strong> | Heading: <strong>${props.heading_deg}°</strong></div>
              <div>Length: <strong>${props.length_m} m</strong> | Gear: <strong>${props.gear_type}</strong></div>
              <div>Status: <span style="color: #36bab8; font-weight: 600;">${props.status}</span></div>
            </div>
            <div style="font-size: 8.5px; color: #797267; margin-top: 3px;">Source: Coastal AIS Feed (Mock)</div>
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
