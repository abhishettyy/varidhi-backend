'use client';

import React, { useState, useEffect } from 'react';
import { AuthorityHeader } from './AuthorityHeader';
import { AuthorityMap } from './AuthorityMap';
import { RegionalStatus } from './RegionalStatus';
import { AlertPanel } from './AlertPanel';
import { ActivityPanel } from './ActivityPanel';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { AUTHORITY_QUICK_PROMPTS } from '@/services/api/chatApi';
import { fetchFishingZones } from '@/services/api/marineApi';
import {
  getMockZones,
  getMockUserLocation,
  getMockRestrictionsGeoJSON,
  getMockVesselsGeoJSON,
  getMockCycloneGeoJSON,
  getMockWeatherGeoJSON,
} from '@/services/api/mockData';
import { FishingZone } from '@/types/marine';

export const AuthorityWorkspace: React.FC = () => {
  const [zones, setZones] = useState<FishingZone[]>(() => getMockZones());
  const userLocation = getMockUserLocation();
  const restrictionsData = getMockRestrictionsGeoJSON();
  const vesselsData = getMockVesselsGeoJSON();
  const cycloneData = getMockCycloneGeoJSON();
  const weatherData = getMockWeatherGeoJSON();

  const [selectedZone, setSelectedZone] = useState<FishingZone | null>(null);
  const [activeTab, setActiveTab] = useState<'monitoring' | 'chat' | 'fleet'>('monitoring');

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

  const handleSelectZone = (zone: FishingZone) => {
    setSelectedZone(zone);
  };

  const handleFocusArea = (key: string) => {
    const found = zones.find((z) => z.id === key);
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
      {/* 1. Authority Telemetry Header */}
      <AuthorityHeader activeAlertsCount={3} />

      {/* 2. Body Split: Regional Operations Panel + Regional Marine Map */}
      <div style={{ flex: 1, display: 'flex', position: 'relative', overflow: 'hidden' }}>
        {/* Left Side: Operations Center Panel */}
        <aside
          style={{
            width: '450px',
            maxWidth: '100%',
            height: '100%',
            backgroundColor: '#f6f3f1',
            borderRight: '1px solid #cecac8',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 10,
          }}
        >
          {/* Tab Navigation */}
          <div
            style={{
              padding: '14px 16px 10px 16px',
              borderBottom: '1px solid #cecac8',
              display: 'flex',
              gap: '8px',
              backgroundColor: '#f6f3f1',
            }}
          >
            <button
              type="button"
              onClick={() => setActiveTab('monitoring')}
              style={{
                flex: 1,
                padding: '8px 10px',
                borderRadius: '100px',
                fontSize: '11px',
                fontWeight: 500,
                border: activeTab === 'monitoring' ? 'none' : '1px solid #cecac8',
                backgroundColor: activeTab === 'monitoring' ? '#242424' : '#ffffff',
                color: activeTab === 'monitoring' ? '#f6f3f1' : '#767371',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                fontFamily: 'inherit',
              }}
            >
              Operations
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('chat')}
              style={{
                flex: 1,
                padding: '8px 10px',
                borderRadius: '100px',
                fontSize: '11px',
                fontWeight: 500,
                border: activeTab === 'chat' ? 'none' : '1px solid #cecac8',
                backgroundColor: activeTab === 'chat' ? '#242424' : '#ffffff',
                color: activeTab === 'chat' ? '#f6f3f1' : '#767371',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                fontFamily: 'inherit',
              }}
            >
              AI Assistant
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('fleet')}
              style={{
                flex: 1,
                padding: '8px 10px',
                borderRadius: '100px',
                fontSize: '11px',
                fontWeight: 500,
                border: activeTab === 'fleet' ? 'none' : '1px solid #cecac8',
                backgroundColor: activeTab === 'fleet' ? '#242424' : '#ffffff',
                color: activeTab === 'fleet' ? '#f6f3f1' : '#767371',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                fontFamily: 'inherit',
              }}
            >
              Fleet AIS
            </button>
          </div>

          {/* Panel Body */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', backgroundColor: '#f6f3f1' }}>
            {activeTab === 'monitoring' && (
              <>
                <RegionalStatus />
                <AlertPanel onFocusArea={handleFocusArea} />
                <ActivityPanel />
              </>
            )}

            {activeTab === 'chat' && (
              <ChatPanel
                role="maritime_operator"
                quickPrompts={AUTHORITY_QUICK_PROMPTS}
                title="Authority Intelligence"
                subtitle="Interrogate regional risk, vessel activity, and alerts"
                defaultExpanded={true}
                onFocusZone={handleFocusArea}
              />
            )}

            {activeTab === 'fleet' && (
              <>
                <ActivityPanel />
                <RegionalStatus />
              </>
            )}
          </div>
        </aside>

        {/* Right Side: Map Canvas */}
        <main style={{ flex: 1, position: 'relative', height: '100%' }}>
          <AuthorityMap
            zones={zones}
            userLocation={userLocation}
            restrictionsData={restrictionsData}
            vesselsData={vesselsData}
            cycloneData={cycloneData}
            weatherData={weatherData}
            selectedZoneId={selectedZone?.id}
            onSelectZone={handleSelectZone}
          />
        </main>
      </div>
    </div>
  );
};
