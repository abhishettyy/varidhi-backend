'use client';

import React from 'react';
import { MarineMap } from '@/components/map/MarineMap';
import { ZoneLayer } from '@/components/map/ZoneLayer';
import { RestrictionLayer } from '@/components/map/RestrictionLayer';
import { VesselLayer } from '@/components/map/VesselLayer';
import { CycloneLayer } from '@/components/map/CycloneLayer';
import { WeatherLayer } from '@/components/map/WeatherLayer';
import { UserLocationMarker } from '@/components/map/UserLocationMarker';
import { MapControls } from '@/components/map/MapControls';
import { MapLegend } from '@/components/map/MapLegend';
import { FishingZone, UserLocation } from '@/types/marine';

interface AuthorityMapProps {
  zones: FishingZone[];
  userLocation: UserLocation;
  restrictionsData: GeoJSON.FeatureCollection;
  vesselsData: GeoJSON.FeatureCollection;
  cycloneData: GeoJSON.FeatureCollection;
  weatherData: GeoJSON.FeatureCollection;
  selectedZoneId?: string;
  onSelectZone: (zone: FishingZone) => void;
}

export const AuthorityMap: React.FC<AuthorityMapProps> = ({
  zones,
  userLocation,
  restrictionsData,
  vesselsData,
  cycloneData,
  weatherData,
  selectedZoneId,
  onSelectZone,
}) => {
  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', overflow: 'hidden' }}>
      <MarineMap
        initialCenter={[userLocation.longitude - 0.2, userLocation.latitude + 0.05]}
        initialZoom={8.8}
      >
        {/* 1. Marine Protected Areas & Sanctuaries (Mulki MPA) */}
        <RestrictionLayer data={restrictionsData} visible={true} />

        {/* 2. Candidate Zones (Monitoring Zone A Risk and Zone C Sanctuary) */}
        <ZoneLayer
          zones={zones}
          selectedZoneId={selectedZoneId}
          onSelectZone={onSelectZone}
          visible={true}
        />

        {/* 3. Live AIS Coastal Vessels & Interceptors */}
        <VesselLayer data={vesselsData} visible={true} />

        {/* 4. Cyclonic Storm Track & Gale Buffer */}
        <CycloneLayer data={cycloneData} visible={true} />

        {/* 5. Marine Weather & Vector Arrows */}
        <WeatherLayer data={weatherData} visible={true} />

        {/* 6. Mangalore Port Control Anchor */}
        <UserLocationMarker location={userLocation} visible={true} />

        {/* Floating Controls */}
        <MapControls
          userLocationCoords={[userLocation.longitude, userLocation.latitude]}
          zones={zones}
        />

        <MapLegend />
      </MarineMap>
    </div>
  );
};
