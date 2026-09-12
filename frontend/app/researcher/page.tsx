'use client';

import React, { useState, useEffect } from 'react';
import { MarineMap } from '@/components/map/MarineMap';
import { ZoneLayer } from '@/components/map/ZoneLayer';
import { PFZLayer } from '@/components/map/PFZLayer';
import { RestrictionLayer } from '@/components/map/RestrictionLayer';
import { UserLocationMarker } from '@/components/map/UserLocationMarker';
import { LayerSwitcher } from '@/components/map/LayerSwitcher';
import { MapLegend } from '@/components/map/MapLegend';
import { MapControls } from '@/components/map/MapControls';
import { ResearcherHeader } from '@/components/researcher/ResearcherHeader';
import { ZoneDetailDrawer } from '@/components/researcher/ZoneDetailDrawer';
import { WeatherLayer } from '@/components/map/WeatherLayer';
import { VesselLayer } from '@/components/map/VesselLayer';
import { CycloneLayer } from '@/components/map/CycloneLayer';
import { TimeSlider } from '@/components/researcher/TimeSlider';
import { OceanTimeSeries } from '@/components/researcher/OceanTimeSeries';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { RESEARCHER_QUICK_PROMPTS } from '@/services/api/chatApi';
import {
  getMockZones,
  getMockUserLocation,
  getMockPfzGeoJSON,
  getMockRestrictionsGeoJSON,
  getMockWeatherGeoJSON,
  getMockVesselsGeoJSON,
  getMockCycloneGeoJSON,
} from '@/services/api/mockData';
import { FishingZone, UserLocation } from '@/types/marine';
import { LayerVisibility } from '@/types/map';
import { GeocodingResult } from '@/services/geocoding/types';
import { fetchFishingZones } from '@/services/api/marineApi';
import { TrendingUp } from 'lucide-react';

export default function ResearcherWorkspace() {
  const [zones, setZones] = useState<FishingZone[]>(() => getMockZones());
  const [pfzData] = useState<GeoJSON.FeatureCollection>(getMockPfzGeoJSON());
  const [restrictionsData] = useState<GeoJSON.FeatureCollection>(getMockRestrictionsGeoJSON());
  const [weatherData] = useState<GeoJSON.FeatureCollection>(getMockWeatherGeoJSON());
  const [vesselData] = useState<GeoJSON.FeatureCollection>(getMockVesselsGeoJSON());
  const [cycloneData] = useState<GeoJSON.FeatureCollection>(getMockCycloneGeoJSON());

  const [userLocation, setUserLocation] = useState<UserLocation>(getMockUserLocation());
  const [selectedZone, setSelectedZone] = useState<FishingZone | null>(null);
  const [showTimeSeries, setShowTimeSeries] = useState<boolean>(false);

  useEffect(() => {
    let mounted = true;
    fetchFishingZones(userLocation.latitude, userLocation.longitude).then((backendZones) => {
      if (mounted && backendZones.length > 0) {
        setZones(backendZones);
      }
    });
    return () => {
      mounted = false;
    };
  }, [userLocation.latitude, userLocation.longitude]);


  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    pfz: true,
    zones: true,
    restrictions: true,
    userLocation: true,
    sst: false,
    chlorophyll: false,
    weather: true,
    vessels: true,
    cyclone: true,
  });

  const handleSelectLocation = (result: GeocodingResult) => {
    setUserLocation({
      name: result.display_name,
      state: result.state || '',
      country: result.country,
      latitude: result.latitude,
      longitude: result.longitude,
      is_default: false,
    });
  };

  const handleFocusZoneById = (zoneId: string) => {
    const found = zones.find((z) => z.id === zoneId);
    if (found) setSelectedZone(found);
  };

  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f6f3f1',
        color: '#242424',
        position: 'relative',
        overflow: 'hidden',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* Top Telemetry Header */}
      <ResearcherHeader
        currentLocationName={userLocation.name}
        onSelectLocation={handleSelectLocation}
        zoneCount={zones.length}
      />

      {/* MapLibre GIS Canvas Viewport */}
      <main
        style={{
          flex: 1,
          position: 'relative',
          margin: '12px 20px 16px 20px',
          borderRadius: '24px',
          overflow: 'hidden',
          border: '1px solid #cecac8',
          boxShadow: '0 4px 20px rgba(36, 36, 36, 0.06)',
        }}
      >
        <MarineMap
          initialCenter={[userLocation.longitude - 0.14, userLocation.latitude + 0.02]}
          initialZoom={9.2}
        >
          {/* Spatial Layers */}
          <RestrictionLayer
            data={restrictionsData}
            visible={layerVisibility.restrictions}
          />

          <PFZLayer
            data={pfzData}
            visible={layerVisibility.pfz}
          />

          <ZoneLayer
            zones={zones}
            selectedZoneId={selectedZone?.id}
            onSelectZone={(zone) => setSelectedZone(zone)}
            visible={layerVisibility.zones}
          />

          <WeatherLayer
            data={weatherData}
            visible={layerVisibility.weather}
          />

          <VesselLayer
            data={vesselData}
            visible={layerVisibility.vessels}
          />

          <CycloneLayer
            data={cycloneData}
            visible={layerVisibility.cyclone}
          />

          <UserLocationMarker
            location={userLocation}
            visible={layerVisibility.userLocation}
          />

          {/* Floating UI HUD Components */}
          {/* Candidate Zone Quick Selector */}
          <div
            style={{
              position: 'absolute',
              top: 16,
              left: '50%',
              transform: 'translateX(-50%)',
              zIndex: 10,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              backgroundColor: '#f6f3f1',
              borderRadius: '100px',
              border: '1px solid #cecac8',
              boxShadow: '0 4px 16px rgba(36, 36, 36, 0.08)',
            }}
          >
            <span
              style={{
                fontSize: '10px',
                color: '#767371',
                fontWeight: 600,
                textTransform: 'uppercase',
                marginRight: '2px',
                letterSpacing: '0.05em',
              }}
            >
              ZONES:
            </span>
            {zones.map((z) => {
              const isSelected = selectedZone?.id === z.id;
              return (
                <button
                  key={z.id}
                  onClick={() => setSelectedZone(z)}
                  title={`Inspect ${z.name}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 14px',
                    borderRadius: '100px',
                    fontSize: '11px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    border: isSelected ? 'none' : '1px solid #cecac8',
                    backgroundColor: isSelected ? '#242424' : '#ffffff',
                    color: isSelected ? '#f6f3f1' : '#242424',
                    transition: 'all 0.15s ease',
                    fontFamily: 'inherit',
                  }}
                >
                  <span
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      backgroundColor: z.status === 'recommended' ? '#2b59d1' : z.status === 'high_risk' ? '#ff9473' : '#767371',
                    }}
                  />
                  <span>{z.code}</span>
                  <span style={{ fontSize: '10px', opacity: isSelected ? 0.9 : 0.6 }}>
                    ({z.status === 'recommended' ? 'Rec' : z.status === 'high_risk' ? 'Risk' : 'Restr'})
                  </span>
                </button>
              );
            })}

            {/* Toggle Time Series Button */}
            <button
              type="button"
              onClick={() => setShowTimeSeries(!showTimeSeries)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                borderRadius: '100px',
                fontSize: '11px',
                fontWeight: 500,
                cursor: 'pointer',
                border: showTimeSeries ? 'none' : '1px solid #cecac8',
                backgroundColor: showTimeSeries ? '#2b59d1' : '#ffffff',
                color: showTimeSeries ? '#f6f3f1' : '#242424',
                marginLeft: '4px',
                transition: 'all 0.15s ease',
                fontFamily: 'inherit',
              }}
            >
              <TrendingUp size={13} />
              <span>TIME-SERIES</span>
            </button>
          </div>

          <LayerSwitcher
            visibility={layerVisibility}
            onChange={setLayerVisibility}
          />

          <MapLegend />

          <MapControls
            userLocationCoords={[userLocation.longitude, userLocation.latitude]}
            zones={zones}
          />

          {/* TimeSlider Docked at Bottom Center */}
          <div
            style={{
              position: 'absolute',
              bottom: 24,
              left: '50%',
              transform: 'translateX(-50%)',
              zIndex: 10,
              width: 'min(90%, 560px)',
            }}
          >
            <TimeSlider />
          </div>

          {/* Floating Time-Series Analytics Box if toggled */}
          {showTimeSeries && (
            <div
              style={{
                position: 'absolute',
                top: 70,
                left: 20,
                zIndex: 20,
                width: '380px',
              }}
            >
              <OceanTimeSeries
                zone={selectedZone || zones[0]}
                onClose={() => setShowTimeSeries(false)}
              />
            </div>
          )}

          {/* Floating Ask Varidhi AI Chat Widget */}
          <div
            style={{
              position: 'absolute',
              bottom: 24,
              right: 20,
              zIndex: 25,
              width: '400px',
              maxWidth: 'calc(100vw - 40px)',
            }}
          >
            <ChatPanel
              role="researcher"
              quickPrompts={RESEARCHER_QUICK_PROMPTS}
              title="Researcher Intelligence"
              subtitle="Interrogate PFZ SST models & gradients"
              defaultExpanded={false}
              onFocusZone={handleFocusZoneById}
            />
          </div>

          {/* Zone Decision & Evidence Inspector Drawer */}
          <ZoneDetailDrawer
            zone={selectedZone}
            onClose={() => setSelectedZone(null)}
          />
        </MarineMap>
      </main>
    </div>
  );
}
