'use client';

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import dynamic from 'next/dynamic';
import type { FeatureCollection } from 'geojson';
import { FishermanHeader } from './FishermanHeader';
import { RecommendationCard } from './RecommendationCard';
import { AlternativeZoneCard } from './AlternativeZoneCard';
import { SafetyCard } from './SafetyCard';
import { SeaConditions } from './SeaConditions';
import { QuickActions } from './QuickActions';
import { WhyRecommendation } from './WhyRecommendation';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { MapHud } from '@/components/console/MapHud';
import { SpotCard } from '@/components/console/SpotCard';
import type { Conditions, MapApi, SpotEvent } from '@/components/console/types';
import { OVERLAYS } from '@/lib/marine/data';
import { coastLon, compass, sampleField, seaState } from '@/lib/marine/field';
import type { FieldKey, LatLon, MarkerKey } from '@/lib/marine/types';
import { FISHERMAN_QUICK_PROMPTS } from '@/services/api/chatApi';
import { fetchFishingZones } from '@/services/api/marineApi';
import { getMockZones, getMockUserLocation } from '@/services/api/mockData';
import { FishingZone } from '@/types/marine';
import { Drawer } from '@/components/common/Drawer';
import { MessageSquare, Wind, Waves, Compass, Thermometer, Sparkles } from 'lucide-react';

// Leaflet canvas particle map dynamically imported without SSR
const MarineMapLeaflet = dynamic(() => import('@/components/map/MarineMapLeaflet'), {
  ssr: false,
  loading: () => (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'grid',
        placeItems: 'center',
        backgroundColor: '#dceef3',
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            border: '3px solid #087ea4',
            borderTopColor: 'transparent',
            animation: 'varSpin 1s linear infinite',
          }}
        />
        <span className="shimmer-text" style={{ fontFamily: 'var(--font-abc-diatype-mono), monospace', fontSize: '11px', fontWeight: 600, letterSpacing: '0.12em' }}>
          LOADING MARINE CARTOGRAPHY & PARTICLE VECTOR ENGINE...
        </span>
      </div>
    </div>
  ),
});

/* A believable outbound track: boats leave the fairway heading seaward and
   then curve onto their bearing, so a dead-straight line looks wrong. This is
   a quadratic Bézier bowed to the west, with every point held offshore of the
   shoreline. */
function curvedVoyage(from: LatLon, to: LatLon, steps = 56): [number, number][] {
  const dx = to.lon - from.lon;
  const dy = to.lat - from.lat;
  const leg = Math.hypot(dx, dy);
  const cLon = (from.lon + to.lon) / 2 - leg * 0.34; // bow out to sea
  const cLat = (from.lat + to.lat) / 2 + dy * 0.06;
  const pts: [number, number][] = [];
  for (let i = 0; i <= steps; i++) {
    const u = i / steps;
    const k = 1 - u;
    const lat = k * k * from.lat + 2 * k * u * cLat + u * u * to.lat;
    const lon = k * k * from.lon + 2 * k * u * cLon + u * u * to.lon;
    // never let the track cut across the beach
    pts.push([Math.min(lon, coastLon(lat) - 0.004), lat]);
  }
  return pts;
}

export const FishermanWorkspace: React.FC = () => {
  const [zones, setZones] = useState<FishingZone[]>(() => getMockZones());
  const userLocation = getMockUserLocation();

  const [selectedZone, setSelectedZone] = useState<FishingZone>(() => {
    const defaultZones = getMockZones();
    return defaultZones.find((z) => z.id === 'ZONE_B') || defaultZones[0];
  });
  const [showWhyModal, setShowWhyModal] = useState(false);
  const [showAlertsDrawer, setShowAlertsDrawer] = useState(false);
  const [activeTab, setActiveTab] = useState<'advisory' | 'chat' | 'conditions'>('advisory');

  // Marine Map & Particle Engine State
  const [overlay, setOverlay] = useState<FieldKey>('waves');
  const [simple, setSimple] = useState<boolean>(true);
  const [particles, setParticles] = useState<boolean>(true);
  const [values, setValues] = useState<boolean>(false);
  const [markers, setMarkers] = useState<Record<MarkerKey, boolean>>({
    pfz: true,
    risk: true,
    restricted: true,
    cyclone: true,
    vessels: true,
  });
  const [home, setHome] = useState<LatLon>({
    lat: userLocation.latitude,
    lon: userLocation.longitude,
  });
  const [spot, setSpot] = useState<SpotEvent | null>(null);
  const [features, setFeatures] = useState<FeatureCollection | null>(null);
  const [pendingQuery, setPendingQuery] = useState<string | null>(null);
  const [dataVersion, setDataVersion] = useState(0);

  const mapApi = useRef<MapApi | null>(null);

  // Live simulation tick
  const [t, setT] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setT((prev) => prev + 0.05), 1000);
    return () => clearInterval(id);
  }, []);

  // Fetch real backend fishing zones from P5/P6
  useEffect(() => {
    let mounted = true;
    fetchFishingZones(userLocation.latitude, userLocation.longitude).then((backendZones) => {
      if (mounted && backendZones.length > 0) {
        setZones(backendZones);
        const rec = backendZones.find((z) => z.id === 'ZONE_B' || z.status === 'recommended') || backendZones[0];
        setSelectedZone(rec);
      }
    });
    return () => {
      mounted = false;
    };
  }, [userLocation.latitude, userLocation.longitude]);

  // Zone B is the recommended zone
  const recommendedZone = zones.find((z) => z.id === 'ZONE_B' || z.status === 'recommended') || zones[0];
  const alternativeZones = zones.filter((z) => z.id !== recommendedZone.id);

  const handleSelectZone = useCallback((zone: FishingZone) => {
    setSelectedZone(zone);
    if (mapApi.current && zone.coordinates) {
      const [zLon, zLat] = zone.coordinates;
      mapApi.current.panTo({ lat: zLat, lon: zLon }, 11);
    }
  }, []);

  const handleFocusZoneById = useCallback((zoneId: string) => {
    const found = zones.find((z) => z.id === zoneId);
    if (found) handleSelectZone(found);
  }, [zones, handleSelectZone]);

  // Calculate live conditions at home / boat position for the HUD
  const homeConditions: Conditions = useMemo(() => {
    const wv = sampleField('waves', home.lon, home.lat, t, 0);
    const wd = sampleField('wind', home.lon, home.lat, t, 0);
    const cu = sampleField('currents', home.lon, home.lat, t, 0);
    const st = sampleField('sst', home.lon, home.lat, t, 0);
    return {
      wave: wv.v,
      swell: compass(wv.u, wv.w),
      windKmh: Math.round(wd.v * 3.6),
      current: cu.v,
      sst: st.v,
      state: seaState(wv.v),
    };
  }, [home.lat, home.lon, t]);

  const handleSpotSample = useCallback(
    (key: FieldKey, lon: number, lat: number) => sampleField(key, lon, lat, t, 0),
    [t]
  );

  /* COMMENCE VOYAGE — plot the outbound track to the recommended ground and
     drop it on the chart. */
  const handleCommenceVoyage = useCallback(() => {
    if (!recommendedZone?.coordinates) return;
    const [zLon, zLat] = recommendedZone.coordinates;
    const track = curvedVoyage(home, { lat: zLat, lon: zLon });
    setFeatures({
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: { type: 'LineString', coordinates: track },
          properties: {
            kind: 'route',
            label: `Outbound track · ${recommendedZone.distance_km} km ${recommendedZone.bearing} · ${Math.round((recommendedZone.distance_km / 18.52) * 60)} min at 10 kn`,
          },
        },
        {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [zLon, zLat] },
          properties: { kind: 'ground', label: recommendedZone.name },
        },
      ],
    });
    setSelectedZone(recommendedZone);
  }, [recommendedZone, home]);

  const handleAskSpotConditions = useCallback(() => {
    if (!spot) return;
    const query = `What are the marine conditions and safety assessment at coordinates ${spot.lat.toFixed(3)}°N, ${spot.lon.toFixed(3)}°E? Is it safe to fish there today?`;
    setPendingQuery(query);
    setActiveTab('chat');
    setSpot(null);
  }, [spot]);

  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f6f3f1',
        color: '#242424',
        overflow: 'hidden',
        fontFamily: 'var(--font-sans), sans-serif',
      }}
    >
      {/* 1. Header */}
      <FishermanHeader
        locationName={`${userLocation.name} (${userLocation.state})`}
        onOpenAlerts={() => setShowAlertsDrawer(true)}
      />

      {/* 2. Workspace Body: Map + Action Sidebar */}
      <div className="workspace-body">
        {/* Left Side: Fisherman Action Panel */}
        <aside
          className="workspace-aside"
          style={{
            width: '440px',
            backgroundColor: '#f6f3f1',
            borderRight: '1px solid #cecac8',
            zIndex: 10,
          }}
        >
          {/* Navigation — Segmented Control */}
          <div
            style={{
              padding: '12px 16px',
              borderBottom: '1px solid #cecac8',
              backgroundColor: '#f6f3f1',
            }}
          >
            <div
              style={{
                display: 'flex',
                backgroundColor: '#eeecea',
                borderRadius: '100px',
                padding: '3px',
                gap: '2px',
              }}
            >
              {(['advisory', 'chat', 'conditions'] as const).map((tab) => {
                const labels = { advisory: 'Advisory', chat: 'AI Chat', conditions: 'Telemetry' };
                const active = activeTab === tab;
                return (
                  <button
                    key={tab}
                    type="button"
                    onClick={() => setActiveTab(tab)}
                    style={{
                      flex: 1,
                      padding: '7px 10px',
                      borderRadius: '100px',
                      fontSize: '11px',
                      fontWeight: active ? 600 : 400,
                      border: 'none',
                      backgroundColor: active ? '#ffffff' : 'transparent',
                      color: active ? '#242424' : '#767371',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                    }}
                  >
                    {labels[tab]}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Panel Scrollable Content */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {activeTab === 'advisory' && (
              <>
                <RecommendationCard
                  zone={recommendedZone}
                  onWhyThisZone={() => setShowWhyModal(true)}
                  onNavigate={handleCommenceVoyage}
                />

                {/* Why Modal */}
                {showWhyModal && (
                  <div
                    style={{
                      position: 'fixed',
                      inset: 0,
                      backgroundColor: 'rgba(36, 36, 36, 0.4)',
                      backdropFilter: 'blur(4px)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 1000,
                      padding: '20px',
                    }}
                    onClick={() => setShowWhyModal(false)}
                  >
                    <div
                      style={{
                        backgroundColor: '#f6f3f1',
                        border: '1px solid #cecac8',
                        borderRadius: '12px',
                        maxWidth: '560px',
                        width: '100%',
                        maxHeight: '90vh',
                        overflowY: 'auto',
                        padding: '24px',
                        boxShadow: '0 20px 40px rgba(36,36,36,0.2)',
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <WhyRecommendation
                        zone={recommendedZone}
                        onClose={() => setShowWhyModal(false)}
                      />
                    </div>
                  </div>
                )}

                {/* Alternative Zones List */}
                <div>
                  <div
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                      color: '#767371',
                      marginBottom: '10px',
                    }}
                  >
                    Alternative Options
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {alternativeZones.map((z) => (
                      <AlternativeZoneCard
                        key={z.id}
                        zone={z}
                        onSelect={() => handleSelectZone(z)}
                      />
                    ))}
                  </div>
                </div>
              </>
            )}

            {activeTab === 'chat' && (
              <ChatPanel
                role="fisherman"
                quickPrompts={FISHERMAN_QUICK_PROMPTS}
                title="Fisherman Intelligence"
                subtitle="Ask questions regarding zones, legal checks & sea conditions"
                defaultExpanded={true}
                onFocusZone={handleFocusZoneById}
                onVisualPayload={(payload) => {
                  if (payload?.map_features_geojson) {
                    setFeatures(payload.map_features_geojson);
                  }
                }}
                pendingQuery={pendingQuery}
                onClearPendingQuery={() => setPendingQuery(null)}
              />
            )}

            {activeTab === 'conditions' && (
              <>
                <SeaConditions />
                <SafetyCard />
              </>
            )}
          </div>
        </aside>

        {/* Right Side: Leaflet + Canvas Flow Map */}
        <main className="workspace-main">
          {/* 1. Core Interactive Leaflet Map */}
          <MarineMapLeaflet
            overlay={overlay}
            simple={simple}
            particles={particles}
            values={values}
            t={t}
            hour={0}
            dataVersion={dataVersion}
            markers={markers}
            home={home}
            features={features}
            backendZones={zones}
            selectedZoneId={selectedZone?.id}
            onSelectZone={handleSelectZone}
            onHomeChange={setHome}
            onSpot={setSpot}
            apiRef={mapApi}
          />

          {/* 2. Floating Marine HUD (GPS Position, Conditions & Zoom) */}
          <MapHud
            overlay={overlay}
            simple={simple}
            particles={particles}
            timeTag="LIVE NOW"
            home={home}
            cond={homeConditions}
            onLocate={() => {
              const defaultLoc = { lat: userLocation.latitude, lon: userLocation.longitude };
              setHome(defaultLoc);
              mapApi.current?.panTo(defaultLoc, 10);
            }}
            onZoom={(d) => mapApi.current?.zoomBy(d)}
          />

          {/* 3. Floating Overlay Toolbar (Waves, Wind, Currents, SST, Chl-a) */}
          <div
            style={{
              position: 'absolute',
              top: 14,
              right: 68,
              zIndex: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(8px)',
              padding: '4px 6px',
              borderRadius: '10px',
              border: '1px solid #d8e9ee',
              boxShadow: '0 4px 14px rgba(18, 49, 59, 0.09)',
            }}
          >
            {OVERLAYS.map((o) => {
              const active = overlay === o.key;
              return (
                <button
                  key={o.key}
                  type="button"
                  onClick={() => setOverlay(o.key)}
                  style={{
                    padding: '5px 10px',
                    borderRadius: '7px',
                    fontSize: '11px',
                    fontWeight: active ? 600 : 500,
                    border: 'none',
                    backgroundColor: active ? '#087ea4' : 'transparent',
                    color: active ? '#ffffff' : '#607d86',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <span
                    style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: active ? '#ffffff' : o.swatch,
                    }}
                  />
                  <span>{o.label}</span>
                </button>
              );
            })}

            {/* Particle Flow Toggle */}
            <div style={{ width: '1px', height: '18px', backgroundColor: '#d8e9ee', margin: '0 2px' }} />
            <button
              type="button"
              onClick={() => setParticles((p) => !p)}
              title={particles ? "Turn off vector flow arrows" : "Turn on vector flow arrows"}
              style={{
                padding: '5px 8px',
                borderRadius: '7px',
                fontSize: '10.5px',
                fontWeight: particles ? 600 : 500,
                border: 'none',
                backgroundColor: particles ? '#e3f7f8' : 'transparent',
                color: particles ? '#087ea4' : '#8fa7b0',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <Wind size={12} />
              <span>Flow</span>
            </button>
          </div>

          {/* 4. Click Spot Inspector Card */}
          {spot && (
            <SpotCard
              spot={spot}
              sample={handleSpotSample}
              onClose={() => setSpot(null)}
              onSetHome={() => {
                setHome({ lat: spot.lat, lon: spot.lon });
                setSpot(null);
              }}
              onAsk={handleAskSpotConditions}
            />
          )}

          {/* 5. Floating Bottom AI & Selected Zone Bar */}
          <div
            style={{
              position: 'absolute',
              bottom: 24,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 'min(92%, 560px)',
              zIndex: 600,
            }}
          >
            <div
              style={{
                padding: '10px 12px 10px 20px',
                backgroundColor: 'rgba(255, 255, 255, 0.96)',
                backdropFilter: 'blur(12px)',
                border: '1px solid #d8e9ee',
                borderRadius: '100px',
                boxShadow: '0 12px 32px rgba(18, 49, 59, 0.16)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                <div
                  style={{
                    width: 9,
                    height: 9,
                    borderRadius: '50%',
                    backgroundColor: selectedZone?.status === 'recommended' ? '#3faf8f' : selectedZone?.status === 'restricted' ? '#d6334c' : '#e8a93c',
                    flexShrink: 0,
                    boxShadow: '0 0 0 3px rgba(8,126,164,0.15)',
                  }}
                />
                <span
                  style={{
                    fontSize: '12.5px',
                    color: '#12313b',
                    fontWeight: 600,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {selectedZone?.name} · {selectedZone?.distance_km} km {selectedZone?.bearing || ''}
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    padding: '2px 7px',
                    borderRadius: '100px',
                    backgroundColor: selectedZone?.status === 'recommended' ? '#e6f6f0' : '#fdf3e1',
                    color: selectedZone?.status === 'recommended' ? '#2a8a6e' : '#a86b12',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                  }}
                >
                  {selectedZone?.status}
                </span>
              </div>

              <button
                type="button"
                onClick={() => setActiveTab('chat')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '11px',
                  fontWeight: 600,
                  padding: '8px 18px',
                  borderRadius: '100px',
                  backgroundColor: '#087ea4',
                  color: '#ffffff',
                  border: 'none',
                  cursor: 'pointer',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  transition: 'opacity 0.15s ease, transform 0.15s ease',
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '0.9';
                  e.currentTarget.style.transform = 'scale(1.02)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <Sparkles size={13} />
                <span>Ask AI Assistant ▸</span>
              </button>
            </div>
          </div>
        </main>
      </div>

      {/* Safety Alerts Drawer */}
      <Drawer
        isOpen={showAlertsDrawer}
        onClose={() => setShowAlertsDrawer(false)}
        title="Official Marine Advisories"
        subtitle="IMD, INCOIS & Karnataka Fisheries Department"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <SafetyCard />
          <SeaConditions />
        </div>
      </Drawer>
    </div>
  );
};
