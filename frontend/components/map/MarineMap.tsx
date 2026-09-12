'use client';

import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import type { Map as MapLibreMap } from 'maplibre-gl';

interface MapContextType {
  map: MapLibreMap | null;
  isLoaded: boolean;
}

const MapContext = createContext<MapContextType>({
  map: null,
  isLoaded: false,
});

export const useMarineMap = () => useContext(MapContext);

interface MarineMapProps {
  children?: React.ReactNode;
  initialCenter?: [number, number]; // [longitude, latitude]
  initialZoom?: number;
  onMapClick?: () => void;
}

// High-performance, dedicated marine ocean basemap using ESRI World Ocean Base + Reference
// Features authentic bathymetry depth gradients, marine blue coastal tints, zero API keys, and full CORS support
const MARINE_DARK_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    esriOceanBase: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      maxzoom: 10, // Instruct MapLibre to gracefully overzoom level 10 bathymetry tiles so "data not available" never appears
      attribution: '© Esri, GEBCO, NOAA, National Geographic, DeLorme, HERE | Varidhi Marine GIS',
    },
    esriOceanReference: {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      maxzoom: 10,
    },
  },
  glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
  layers: [
    {
      id: 'abyss-ocean-floor',
      type: 'background',
      paint: {
        'background-color': '#071830', // Deep marine abyss blue
      },
    },
    {
      id: 'esri-ocean-base-tiles',
      type: 'raster',
      source: 'esriOceanBase',
      minzoom: 0,
      maxzoom: 18,
      paint: {
        'raster-opacity': 1.0,
        'raster-brightness-min': 0.0,
        'raster-brightness-max': 0.98,
        'raster-saturation': 0.55, // Deep, vibrant nautical blue
        'raster-contrast': 0.25,
      },
    },
    {
      id: 'esri-ocean-reference-tiles',
      type: 'raster',
      source: 'esriOceanReference',
      minzoom: 0,
      maxzoom: 18,
      paint: {
        'raster-opacity': 0.85,
      },
    },
  ],
};

export const MarineMap: React.FC<MarineMapProps> = ({
  children,
  initialCenter = [74.68, 12.92], // Coastal waters off Mangalore
  initialZoom = 9.8,
  onMapClick,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [mapInstance, setMapInstance] = useState<MapLibreMap | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainerRef.current || mapInstance) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: MARINE_DARK_STYLE,
      center: initialCenter,
      zoom: initialZoom,
      pitch: 15,
      attributionControl: false,
    });

    // Custom attribution
    map.addControl(
      new maplibregl.AttributionControl({
        compact: true,
        customAttribution: '© OpenStreetMap contributors, CartoDB | Varidhi Marine GIS (SIH 2026)',
      }),
      'bottom-left'
    );

    map.on('load', () => {
      setIsLoaded(true);
      map.resize();
    });

    if (onMapClick) {
      map.on('click', onMapClick);
    }

    setMapInstance(map);

    return () => {
      map.remove();
    };
  }, []);

  useEffect(() => {
    if (!mapInstance || !isLoaded) return;
    mapInstance.flyTo({
      center: initialCenter,
      duration: 1200,
      essential: true,
    });
  }, [initialCenter[0], initialCenter[1], isLoaded]);

  return (
    <MapContext.Provider value={{ map: mapInstance, isLoaded }}>
      <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}>
        <div
          ref={mapContainerRef}
          style={{ width: '100%', height: '100%', outline: 'none' }}
        />
        {isLoaded && children}
      </div>
    </MapContext.Provider>
  );
};
