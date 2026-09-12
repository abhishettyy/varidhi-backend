'use client';

import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { useMarineMap } from './MarineMap';
import { FishingZone } from '@/types/marine';

interface ZoneLayerProps {
  zones: FishingZone[];
  selectedZoneId?: string | null;
  onSelectZone: (zone: FishingZone) => void;
  visible?: boolean;
}

export const ZoneLayer: React.FC<ZoneLayerProps> = ({
  zones,
  selectedZoneId,
  onSelectZone,
  visible = true,
}) => {
  const { map, isLoaded } = useMarineMap();
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!map || !isLoaded) return;

    // Clear existing markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    zones.forEach((zone) => {
      const isSelected = zone.id === selectedZoneId;
      const isRec = zone.status === 'recommended';
      const isRisk = zone.status === 'high_risk';
      const isRestr = zone.status === 'restricted';

      const color = isRec ? '#10b981' : isRisk ? '#ef4444' : isRestr ? '#818cf8' : '#f59e0b';
      const bgColor = isRec ? '#065f46' : isRisk ? '#991b1b' : isRestr ? '#1e1b4b' : '#78350f';

      // Create interactive DOM element for Zone Marker
      const el = document.createElement('div');
      el.className = 'zone-marker-container';
      el.style.display = visible ? 'flex' : 'none';
      el.style.flexDirection = 'column';
      el.style.alignItems = 'center';
      el.style.cursor = 'pointer';
      el.style.transform = 'translate(-50%, -50%)';

      // Halo & Core Circle
      const circleContainer = document.createElement('div');
      circleContainer.style.position = 'relative';
      circleContainer.style.width = isSelected ? '34px' : '26px';
      circleContainer.style.height = isSelected ? '34px' : '26px';
      circleContainer.style.display = 'flex';
      circleContainer.style.alignItems = 'center';
      circleContainer.style.justifyContent = 'center';
      circleContainer.style.transition = 'all 0.2s ease';

      const halo = document.createElement('div');
      halo.style.position = 'absolute';
      halo.style.width = '100%';
      halo.style.height = '100%';
      halo.style.borderRadius = '50%';
      halo.style.backgroundColor = color;
      halo.style.opacity = isSelected ? '0.45' : '0.25';
      halo.style.boxShadow = `0 0 14px ${color}`;

      const core = document.createElement('div');
      core.style.width = isSelected ? '18px' : '14px';
      core.style.height = isSelected ? '18px' : '14px';
      core.style.borderRadius = '50%';
      core.style.backgroundColor = color;
      core.style.border = '2.5px solid #ffffff';
      core.style.boxShadow = `0 2px 8px rgba(0,0,0,0.5)`;
      core.style.zIndex = '2';

      circleContainer.appendChild(halo);
      circleContainer.appendChild(core);

      // Label Tag under circle
      const tag = document.createElement('div');
      tag.style.marginTop = '4px';
      tag.style.padding = '2px 6px';
      tag.style.borderRadius = '4px';
      tag.style.backgroundColor = 'rgba(5, 10, 20, 0.9)';
      tag.style.border = `1px solid ${isSelected ? '#00e5ff' : color}`;
      tag.style.color = '#ffffff';
      tag.style.fontSize = '10px';
      tag.style.fontWeight = '700';
      tag.style.whiteSpace = 'nowrap';
      tag.style.boxShadow = '0 2px 6px rgba(0,0,0,0.6)';
      tag.innerText = zone.code;

      el.appendChild(circleContainer);
      el.appendChild(tag);

      // Click listener
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        onSelectZone(zone);
      });

      // Hover effects
      el.addEventListener('mouseenter', () => {
        circleContainer.style.transform = 'scale(1.2)';
        tag.style.borderColor = '#00e5ff';
      });
      el.addEventListener('mouseleave', () => {
        circleContainer.style.transform = 'scale(1)';
        tag.style.borderColor = isSelected ? '#00e5ff' : color;
      });

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(zone.coordinates)
        .addTo(map);

      markersRef.current.push(marker);
    });

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
    };
  }, [map, isLoaded, zones, selectedZoneId, visible]);

  return null;
};
