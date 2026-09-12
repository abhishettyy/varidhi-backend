'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';
import { UserLocation } from '@/types/marine';

interface UserLocationMarkerProps {
  location: UserLocation;
  visible?: boolean;
}

export const UserLocationMarker: React.FC<UserLocationMarkerProps> = ({
  location,
  visible = true,
}) => {
  const { map, isLoaded } = useMarineMap();
  const markerRef = useRef<maplibregl.Marker | null>(null);

  useEffect(() => {
    if (!map || !isLoaded) return;

    // Create custom DOM element for nautical port marker
    const el = document.createElement('div');
    el.className = 'port-marker';
    el.title = `User Port: ${location.name}`;

    const ping = document.createElement('div');
    ping.className = 'port-marker-ping';

    const center = document.createElement('div');
    center.className = 'port-marker-center';

    el.appendChild(ping);
    el.appendChild(center);

    const popup = new maplibregl.Popup({ offset: 18, closeButton: false }).setHTML(`
      <div style="font-family: inherit; font-size: 12px; color: #221f1c; padding: 4px 6px;">
        <strong style="color: #221f1c;">⚓ ${location.name}</strong><br/>
        <span style="color: #797267; font-size: 11px;">Coord: ${location.latitude.toFixed(4)}°N, ${location.longitude.toFixed(4)}°E</span>
      </div>
    `);

    const marker = new maplibregl.Marker({ element: el })
      .setLngLat([location.longitude, location.latitude])
      .setPopup(popup)
      .addTo(map);

    markerRef.current = marker;

    return () => {
      marker.remove();
      markerRef.current = null;
    };
  }, [map, isLoaded, location]);

  useEffect(() => {
    if (!markerRef.current) return;
    const element = markerRef.current.getElement();
    if (element) {
      element.style.display = visible ? 'block' : 'none';
    }
  }, [visible]);

  return null;
};
