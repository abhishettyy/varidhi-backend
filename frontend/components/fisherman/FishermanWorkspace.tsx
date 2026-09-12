'use client';

import React, { useState, useEffect } from 'react';
import { FishermanHeader } from './FishermanHeader';
import { FishermanMap } from './FishermanMap';
import { RecommendationCard } from './RecommendationCard';
import { AlternativeZoneCard } from './AlternativeZoneCard';
import { SafetyCard } from './SafetyCard';
import { SeaConditions } from './SeaConditions';
import { QuickActions } from './QuickActions';
import { WhyRecommendation } from './WhyRecommendation';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { FISHERMAN_QUICK_PROMPTS } from '@/services/api/chatApi';
import { fetchFishingZones } from '@/services/api/marineApi';
import {
  getMockZones,
  getMockUserLocation,
  getMockPfzGeoJSON,
  getMockRestrictionsGeoJSON,
  getMockWeatherGeoJSON,
} from '@/services/api/mockData';
import { FishingZone } from '@/types/marine';
import { Drawer } from '@/components/common/Drawer';
import { MessageSquare } from 'lucide-react';

export const FishermanWorkspace: React.FC = () => {
  const [zones, setZones] = useState<FishingZone[]>(() => getMockZones());
  const userLocation = getMockUserLocation();
  const pfzData = getMockPfzGeoJSON();
  const restrictionsData = getMockRestrictionsGeoJSON();
  const weatherData = getMockWeatherGeoJSON();

  const [selectedZone, setSelectedZone] = useState<FishingZone>(() => {
    const defaultZones = getMockZones();
    return defaultZones.find((z) => z.id === 'ZONE_B') || defaultZones[0];
  });
  const [showWhyModal, setShowWhyModal] = useState(false);
  const [showAlertsDrawer, setShowAlertsDrawer] = useState(false);
  const [activeTab, setActiveTab] = useState<'advisory' | 'chat' | 'conditions'>('advisory');

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

  const handleSelectZone = (zone: FishingZone) => {
    setSelectedZone(zone);
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
        overflow: 'hidden',
        fontFamily: 'var(--font-abc-diatype-mono), monospace',
      }}
    >
      {/* 1. Header */}
      <FishermanHeader
        locationName={`${userLocation.name} (${userLocation.state})`}
        onOpenAlerts={() => setShowAlertsDrawer(true)}
      />

      {/* 2. Workspace Body: Map + Action Sidebar */}
      <div style={{ flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
        {/* Left Side: Fisherman Action Panel */}
        <aside
          style={{
            width: '440px',
            maxWidth: '100%',
            height: '100%',
            backgroundColor: '#f6f3f1',
            borderRight: '1px solid #cecac8',
            display: 'flex',
            flexDirection: 'column',
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
                      boxShadow: active ? '0 1px 4px rgba(36,36,36,0.1)' : 'none',
                      fontFamily: 'inherit',
                    }}
                  >
                    {labels[tab]}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tab Content Panels */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {activeTab === 'advisory' && (
              <>
                {/* 1. Quick Prompts / Actions */}
                <QuickActions
                  onTriggerAction={(query) => {
                    setActiveTab('chat');
                  }}
                />

                {/* 2. Top Recommended Destination Card */}
                <RecommendationCard
                  zone={recommendedZone}
                  onWhyThisZone={() => setShowWhyModal(true)}
                  onViewOnMap={() => handleSelectZone(recommendedZone)}
                />

                {/* 3. Why Recommendation Expandable if requested */}
                {showWhyModal && (
                  <WhyRecommendation
                    zone={recommendedZone}
                    onClose={() => setShowWhyModal(false)}
                  />
                )}

                {/* 4. Safety Overview Card */}
                <SafetyCard />

                {/* 5. Alternative / Disqualified Zones List */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span style={{ fontSize: '10px', color: '#767371', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      CANDIDATE ZONES ({alternativeZones.length})
                    </span>
                    <span style={{ fontSize: '10px', color: '#2b59d1', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      SAFETY EVALUATIONS
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
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

        {/* Right Side: MapLibre GIS Map View */}
        <main style={{ flex: 1, position: 'relative', height: '100%' }}>
          <FishermanMap
            zones={zones}
            userLocation={userLocation}
            pfzData={pfzData}
            restrictionsData={restrictionsData}
            weatherData={weatherData}
            selectedZoneId={selectedZone?.id}
            onSelectZone={handleSelectZone}
          />

          {/* Floating AI Query Bar */}
          <div
            style={{
              position: 'absolute',
              bottom: 24,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 'min(92%, 520px)',
              zIndex: 10,
            }}
          >
            <div
              style={{
                padding: '10px 10px 10px 20px',
                backgroundColor: 'rgba(246, 243, 241, 0.96)',
                backdropFilter: 'blur(12px)',
                border: '1px solid #cecac8',
                borderRadius: '100px',
                boxShadow: '0 8px 24px rgba(36, 36, 36, 0.12), 0 2px 8px rgba(36,36,36,0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: '#2b59d1',
                    flexShrink: 0,
                    boxShadow: '0 0 0 3px rgba(43,89,209,0.15)',
                  }}
                />
                <span
                  style={{
                    fontSize: '12px',
                    color: '#242424',
                    fontWeight: 500,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {selectedZone?.name} · {selectedZone?.distance_km} km {selectedZone?.bearing}
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
                  backgroundColor: '#242424',
                  color: '#f6f3f1',
                  border: 'none',
                  cursor: 'pointer',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  transition: 'opacity 0.15s ease, transform 0.15s ease',
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '0.85';
                  e.currentTarget.style.transform = 'scale(1.02)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <MessageSquare size={12} />
                <span>Ask AI ▸</span>
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
