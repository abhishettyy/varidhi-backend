'use client';

import React from 'react';
import { MarineMap } from '@/components/map/MarineMap';
import { ZoneLayer } from '@/components/map/ZoneLayer';
import { PFZLayer } from '@/components/map/PFZLayer';
import { RestrictionLayer } from '@/components/map/RestrictionLayer';
import { UserLocationMarker } from '@/components/map/UserLocationMarker';
import { WeatherLayer } from '@/components/map/WeatherLayer';
import { MapControls } from '@/components/map/MapControls';
import { MapLegend } from '@/components/map/MapLegend';
import { FishingZone, UserLocation } from '@/types/marine';

interface FishermanMapProps {
  zones: FishingZone[];
  userLocation: UserLocation;
  pfzData: GeoJSON.FeatureCollection;
  restrictionsData: GeoJSON.FeatureCollection;
  weatherData?: GeoJSON.FeatureCollection;
  selectedZoneId?: string;
  onSelectZone: (zone: FishingZone) => void;
  showWeather?: boolean;
}

export const FishermanMap: React.FC<FishermanMapProps> = ({
  zones,
  userLocation,
  pfzData,
  restrictionsData,
  weatherData,
  selectedZoneId,
  onSelectZone,
  showWeather = true,
}) => {
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>
      <MarineMap
        initialCenter={[userLocation.longitude - 0.12, userLocation.latitude + 0.02]}
        initialZoom={9.4}
      >
        {/* 1. Protected Marine Sanctuaries (Mulki MPA) */}
        <RestrictionLayer data={restrictionsData} visible={true} />

        {/* 2. INCOIS Potential Fishing Zones */}
        <PFZLayer data={pfzData} visible={true} />

        {/* 3. Candidate Zones (Zone B Recommended, Zone A Risk, Zone C Restricted) */}
        <ZoneLayer
          zones={zones}
          selectedZoneId={selectedZoneId}
          onSelectZone={onSelectZone}
          visible={true}
        />

        {/* 4. Weather Wind Vectors (Directional arrows & wave heights) */}
        {weatherData && <WeatherLayer data={weatherData} visible={showWeather} />}

        {/* 5. User Anchor Location at Mangalore Old Port */}
        <UserLocationMarker location={userLocation} visible={true} />

        {/* Map UI Controls */}
        <MapControls
          userLocationCoords={[userLocation.longitude, userLocation.latitude]}
          zones={zones}
        />

        {/* Status Legend */}
        <MapLegend />
      </MarineMap>
    </div>
  );
};
