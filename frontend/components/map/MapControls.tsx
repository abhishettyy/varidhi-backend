'use client';

import React from 'react';
import { useMarineMap } from './MarineMap';
import { Plus, Minus, Compass, Anchor, Maximize2 } from 'lucide-react';
import { FishingZone } from '@/types/marine';

interface MapControlsProps {
  userLocationCoords?: [number, number]; // [lon, lat]
  zones?: FishingZone[];
}

export const MapControls: React.FC<MapControlsProps> = ({
  userLocationCoords = [74.8360, 12.8550],
  zones = [],
}) => {
  const { map, isLoaded } = useMarineMap();

  const handleZoomIn = () => {
    if (!map) return;
    map.zoomIn({ duration: 300 });
  };

  const handleZoomOut = () => {
    if (!map) return;
    map.zoomOut({ duration: 300 });
  };

  const handleResetNorth = () => {
    if (!map) return;
    map.resetNorthPitch({ duration: 500 });
  };

  const handleCenterPort = () => {
    if (!map) return;
    map.flyTo({
      center: userLocationCoords,
      zoom: 10.5,
      essential: true,
      duration: 1200,
    });
  };

  const handleFitZones = () => {
    if (!map || zones.length === 0) return;
    const allCoords = [
      userLocationCoords,
      ...zones.map((z) => z.coordinates),
    ];

    let minLon = Infinity;
    let maxLon = -Infinity;
    let minLat = Infinity;
    let maxLat = -Infinity;

    allCoords.forEach(([lon, lat]) => {
      if (lon < minLon) minLon = lon;
      if (lon > maxLon) maxLon = lon;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    });

    map.fitBounds(
      [
        [minLon - 0.05, minLat - 0.05],
        [maxLon + 0.05, maxLat + 0.05],
      ],
      {
        padding: { top: 70, bottom: 80, left: 80, right: 340 },
        duration: 1400,
      }
    );
  };

  if (!isLoaded) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        left: 20,
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        padding: '6px',
        backgroundColor: '#f6f3f1',
        borderRadius: '16px',
        border: '1px solid #cecac8',
        boxShadow: '0 4px 16px rgba(36, 36, 36, 0.08)',
      }}
    >
      <button
        onClick={handleZoomIn}
        title="Zoom In"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cecac8',
          color: '#242424',
          padding: '6px',
          borderRadius: '9999px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
      >
        <Plus size={15} />
      </button>

      <button
        onClick={handleZoomOut}
        title="Zoom Out"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cecac8',
          color: '#242424',
          padding: '6px',
          borderRadius: '9999px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
      >
        <Minus size={15} />
      </button>

      <div style={{ height: 1, backgroundColor: '#cecac8', margin: '2px 0' }} />

      <button
        onClick={handleResetNorth}
        title="Reset North Orientation"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cecac8',
          color: '#242424',
          padding: '6px',
          borderRadius: '9999px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
      >
        <Compass size={15} />
      </button>

      <button
        onClick={handleCenterPort}
        title="Fly to Home Port"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cecac8',
          color: '#242424',
          padding: '6px',
          borderRadius: '9999px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
      >
        <Anchor size={15} />
      </button>

      <button
        onClick={handleFitZones}
        title="Fit All Marine Zones"
        style={{
          backgroundColor: '#ffffff',
          border: '1px solid #cecac8',
          color: '#242424',
          padding: '6px',
          borderRadius: '9999px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.15s ease',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#cfdaf5')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#ffffff')}
      >
        <Maximize2 size={15} />
      </button>
    </div>
  );
};
