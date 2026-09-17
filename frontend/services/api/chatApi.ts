import { RoleType, SafetySeverity } from '@/types/marine';
import { AgentResponseData, QuickPrompt } from '@/types/chat';
import { apiClient } from './client';

/**
 * Maps frontend UI role types to the backend RoleType contract.
 */
export function mapRoleToBackend(role: RoleType): string {
  switch (role) {
    case 'fisherman':
      return 'fisherman';
    case 'researcher':
      return 'researcher';
    case 'maritime_operator':
      return 'maritime_operator';
    case 'general':
    default:
      return 'general';
  }
}

/**
 * Normalizes backend AgentResponse into the frontend AgentResponseData format.
 */
function normalizeAgentResponse(data: Partial<AgentResponseData>, role: RoleType): AgentResponseData {
  const visual = { ...(data.visual_payload || {}) };

  // If visual_payload contains map features with zone_ids, extract the top zone_id as focus_zone_id
  if (!visual.focus_zone_id && visual.map_features_geojson) {
    const geojson = visual.map_features_geojson as { features?: Array<{ properties?: { zone_id?: string } }> };
    if (Array.isArray(geojson?.features) && geojson.features.length > 0) {
      const topZone = geojson.features[0]?.properties?.zone_id;
      if (topZone) {
        visual.focus_zone_id = topZone;
      }
    }
  }

  const messageContent = data.message || data.markdown_content || 'No response content received from agent.';

  let keyRecs = Array.isArray(data.key_recommendations) ? data.key_recommendations : [];
  if (keyRecs.length === 0 && data.decision?.action_advice) {
    keyRecs = [data.decision.action_advice];
  }

  let evidenceSummary = Array.isArray(data.evidence_summary) ? data.evidence_summary : [];
  if (evidenceSummary.length === 0 && Array.isArray(data.evidence)) {
    evidenceSummary = data.evidence.map((ev) => `${ev.source}: ${ev.summary}`);
  }

  return {
    response_id: data.response_id || `resp_${Date.now()}`,
    role: (data.role as RoleType) || role,
    message: messageContent,
    markdown_content: messageContent,
    decision: data.decision,
    zones: data.zones || [],
    evidence: data.evidence || [],
    visual_payload: visual,
    query_context: data.query_context,
    telemetry: data.telemetry,
    disclaimer: data.disclaimer,
    safety_alert: data.safety_alert || (data.decision?.safety_level ? {
      severity: (data.decision.safety_level as SafetySeverity) || 'caution_yellow',
      title: data.decision.status === 'SELECTED' ? 'Target Ground Clear & Certified' : 'Operational Caution',
      description: data.decision.action_advice || 'Maintain standard maritime vigilance.',
      action_advice: data.decision.action_advice || 'Proceed with vigilance.',
    } : undefined),
    key_recommendations: keyRecs,
    evidence_summary: evidenceSummary,
    status: data.status || 'success',
    execution_time_seconds: data.execution_time_seconds ?? (data.telemetry?.total_pipeline_ms ? data.telemetry.total_pipeline_ms / 1000 : 0.25),
  };
}

export async function queryVaridhiAI(
  query: string,
  role: RoleType = 'fisherman',
  contextZoneId?: string
): Promise<AgentResponseData> {
  // 1. Try real backend LangGraph agent endpoint first (POST /chat)
  try {
    const backendRole = mapRoleToBackend(role);
    const backendResponse = await apiClient.post<AgentResponseData>('/chat', {
      query,
      role: backendRole,
      context_zone_id: contextZoneId,
    });

    if (backendResponse && (backendResponse.message || backendResponse.markdown_content)) {
      console.info(`[Varidhi API: REAL BACKEND] Received live agent response for "${query}":`, backendResponse);
      return normalizeAgentResponse(backendResponse, role);
    }
  } catch {
    // 2. Try legacy /api/chat/query alias if /chat returned non-200
    try {
      const backendRole = mapRoleToBackend(role);
      const backendResponse = await apiClient.post<AgentResponseData>('/api/chat/query', {
        query,
        role: backendRole,
        context_zone_id: contextZoneId,
      });

      if (backendResponse && (backendResponse.message || backendResponse.markdown_content)) {
        console.info(`[Varidhi API: REAL BACKEND] Received live agent response from alias for "${query}":`, backendResponse);
        return normalizeAgentResponse(backendResponse, role);
      }
    } catch (aliasError) {
      throw new Error(
        `Varidhi backend query failed: ${aliasError instanceof Error ? aliasError.message : String(aliasError)}`,
        { cause: aliasError }
      );
    }
  }

  // The application is backend-driven; never fabricate an advisory when the
  // LangGraph service is unavailable.
  throw new Error('Varidhi backend returned no advisory response.');

  /*
  await new Promise((resolve) => setTimeout(resolve, 200));

  const normalized = query.toLowerCase().trim();

  // ==========================================
  // 1. FISHERMAN PERSONA RESPONSES
  // ==========================================
  if (role === 'fisherman') {
    if (
      normalized.includes('where should i fish') ||
      normalized.includes('best fishing zone') ||
      normalized.includes('recommend') ||
      normalized.includes('where to fish')
    ) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'fisherman',
        message:
          '**Recommended Fishing Zone: Zone B (Netravati Offshore Ground)**\n\nBased on deterministic oceanographic convergence and hydrographic risk evaluation, Zone B (12.90°N, 74.95°E, 8.2 NM SSW) offers the optimal balance of catch opportunity and safety.',
        markdown_content:
          '**Recommended Fishing Zone: Zone B (Netravati Offshore Ground)**\n\nBased on deterministic oceanographic convergence and hydrographic risk evaluation, Zone B (12.90°N, 74.95°E, 8.2 NM SSW) offers the optimal balance of catch opportunity and safety.',
        decision: {
          selected_zone_id: 'ZONE_B',
          status: 'SELECTED',
          opportunity_score: 66.9,
          risk_score: 34.9,
          ranking_score: 67.31,
          regulatory_status: 'ELIGIBLE',
          distance_nm: 8.2,
          bearing: 'SSW',
          species: ['Mackerel', 'Sardines'],
          latitude: 12.90,
          longitude: 74.95,
          reasons: [
            'Regulatory eligibility confirmed (Outside all sanctuaries)',
            'Marine risk score 34.9 is within safe project threshold 50.0',
            'Calculated heuristic ranking score: 67.3',
            'Highest ranking among eligible candidates',
          ],
          safety_level: 'caution_yellow',
          action_advice: 'Favorable relative to evaluated alternatives. Maintain standard maritime vigilance.',
        },
        safety_alert: {
          severity: 'caution_yellow',
          title: 'CAUTION: Moderate Sea Conditions',
          description: 'Wind 11 kts from WSW, wave height 1.1m. Favorable relative to evaluated alternatives.',
          action_advice: 'Favorable relative to evaluated alternatives. Maintain standard maritime vigilance.',
        },
        key_recommendations: [
          'Zone B is located 8.2 NM (15.2 km) SSW from Mangalore harbor entrance.',
          'Target depth is 35 meters along the Netravati thermal gradient.',
          'Expected target species: Indian Mackerel (Rastrelliger) and Sardines.',
          'Outside all marine protected sanctuaries (Legal status: ELIGIBLE).',
        ],
        evidence_summary: [
          'INCOIS PFZ Multi-Satellite Composite indicates active chlorophyll front (2.3 mg/m³).',
          'SST gradient of 0.6°C delta (28.7°C SST) across the 35m bathymetry contour.',
          'Hydrodynamic risk is moderate-low (significant wave height Hs = 1.1m).',
        ],
        visual_payload: {
          focus_zone_id: 'ZONE_B',
          highlight_layer: 'zones',
          metric_badges: {
            Opportunity: '66.9/100',
            Risk: '34.9/100',
            Rank: '67.3/100',
            Distance: '8.2 NM SSW',
            Legal: 'ELIGIBLE',
          },
        },
        status: 'success',
        execution_time_seconds: 0.28,
      };
    }

    if (
      normalized.includes('is it safe') ||
      normalized.includes('safe tomorrow') ||
      normalized.includes('weather') ||
      normalized.includes('safety')
    ) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'fisherman',
        markdown_content:
          '**Safety Status: GOOD TO GO (Morning Window)**\n\nConditions are suitable for small and medium fishing vessels during the early morning window. Winds are expected to slightly strengthen by late afternoon.',
        safety_alert: {
          severity: 'safe_green',
          title: 'Normal Marine Vigilance',
          description: 'Wave height 0.8m to 1.1m, wind speed 11-14 knots from WSW. Swell period 8.2s.',
          action_advice: 'Venture early. Monitor coastal radio channel 16 for afternoon wind updates.',
        },
        key_recommendations: [
          'Morning departure between 04:30 - 05:30 AM is optimal.',
          'Avoid Zone A (Gurupura Shelf) due to rough local rip currents (Hs = 2.7m).',
          'Ensure life jackets and VHF distress beacons are operational.',
        ],
        evidence_summary: [
          'IMD Coastal Forecast: No deep depression or storm warning in southern Karnataka sector.',
          'Wave radar indicates slight sea state in inshore waters.',
        ],
        visual_payload: {
          highlight_layer: 'weather',
          metric_badges: {
            Wave: '0.8 m - 1.1 m',
            Wind: '11 kts (SW)',
            Swell: '8.2 s (Calm)',
            Verdict: 'GOOD TO GO',
          },
        },
        status: 'success',
        execution_time_seconds: 0.22,
      };
    }

    if (
      normalized.includes('why zone b') ||
      normalized.includes('why this zone') ||
      normalized.includes('why recommend')
    ) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'fisherman',
        markdown_content:
          '**Why Varidhi Recommends Zone B:**\n\nZone B balances high biological catch opportunity with legal compliance and safe sea conditions.',
        safety_alert: {
          severity: 'safe_green',
          title: 'All Safety & Legal Checks Passed',
          description: 'No maritime restrictions, low hydrodynamic hazard.',
          action_advice: 'Top-ranked zone across all 5 verification gates.',
        },
        key_recommendations: [
          'PFZ: Strong thermal and chlorophyll convergence detected by INCOIS (2.3 mg/m³).',
          'Sea Conditions: Marine risk score 34.9 is well within the safe threshold (50.0). Wave height 1.1m.',
          'Safety: Calm swell state (8.2s period, safe for mechanized and FRP craft).',
          'Legal Status: 100% open water (clear of Mulki Marine Sanctuary and Naval limits).',
          'Fuel Efficiency: 8.2 NM (15.2 km) run is optimal fuel-to-yield ratio compared to distant grounds.',
        ],
        evidence_summary: [
          'Zone A has opportunity 76.6 but failed safety gate due to marine risk 75.2 (Hs = 2.7m).',
          'Zone C has opportunity 84.5 but failed legal gate (Mulki Protected Sanctuary).',
          'Zone B passed all 5 deterministic decision criteria with rank score 67.31.',
        ],
        visual_payload: {
          focus_zone_id: 'ZONE_B',
          metric_badges: {
            'PFZ Indicator': 'Strong Front (2.3 mg/m³)',
            'Sea State': 'Favorable (1.1m)',
            Restrictions: 'None (ELIGIBLE)',
            Distance: '8.2 NM SSW',
          },
        },
        status: 'success',
        execution_time_seconds: 0.25,
      };
    }

    if (normalized.includes('nearest') || normalized.includes('nearest pfz')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'fisherman',
        markdown_content:
          '**Nearest Recommended Fishing Ground: Zone B (8.2 NM / 15.2 km SSW)**\n\nWhile Zone A is 14.5 NM away, it is currently flagged as High Risk (75.2) due to wave chop. Zone B is the nearest safe and productive ground.',
        key_recommendations: [
          'Head SSW (198°) from Mangalore harbor entrance.',
          'Travel time: approximately 40 mins at 12 knots (8.2 NM).',
        ],
        evidence_summary: ['Distance computed from Mangalore Old Port coordinates (74.83°E, 12.86°N).'],
        visual_payload: {
          focus_zone_id: 'ZONE_B',
          highlight_layer: 'pfz',
          metric_badges: {
            'Nearest Safe': 'Zone B',
            Distance: '8.2 NM SSW',
            Bearing: 'SSW',
          },
        },
        status: 'success',
        execution_time_seconds: 0.21,
      };
    }

    if (normalized.includes('sea conditions') || normalized.includes('conditions') || normalized.includes('wave')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'fisherman',
        markdown_content:
          '**Current Coastal Marine Conditions (Mangalore Sector):**\n\n• Wind: 11 kts from WSW\n• Wave Height: 1.1 m\n• Swell: SW 222°, period 8.2s\n• Current: 0.8 m/s southward\n• Sea Surface Temp: 28.7°C\n• Sea State: Slight to Moderate',
        safety_alert: {
          severity: 'safe_green',
          title: 'Stable Coastal State',
          description: 'Safe navigational parameters in inshore and mid-shelf waters.',
          action_advice: 'Proceed with scheduled trips.',
        },
        key_recommendations: [
          'Currents running southward at 0.8 m/s; account for drift when setting gillnets.',
          'Sea temperature 28.7°C is optimal for epipelagic schooling fish (Mackerel, Sardines).',
        ],
        evidence_summary: ['Aggregated from coastal wave buoys and IMD synoptic station.'],
        visual_payload: {
          highlight_layer: 'weather',
          metric_badges: {
            Wind: '11 kts WSW',
            Waves: '1.1 m',
            Swell: 'SW 222°',
            Current: '0.8 m/s',
            SST: '28.7°C',
            'Sea State': 'Slight',
          },
        },
        status: 'success',
        execution_time_seconds: 0.24,
      };
    }
  }

  // ==========================================
  // 2. MARINE AUTHORITY RESPONSES
  // ==========================================
  if (role === 'maritime_operator' || role === 'general') {
    if (normalized.includes('high-risk') || normalized.includes('risk areas') || normalized.includes('hazards')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'maritime_operator',
        markdown_content:
          '**Regional Risk Assessment: 1 High-Risk Zone Identified**\n\n1. **Zone A (Gurupura Shelf Edge)**: Rough sea hazard ($H_s = 2.7m$, wind 24 kts, current 1.8 m/s, Risk = 75.2). Excluded for artisanal craft.\n2. **Offshore Buffer**: Peripheral swells active beyond 20 NM.',
        safety_alert: {
          severity: 'warning_orange',
          title: 'Small Craft Navigational Warning Active',
          description: 'Artisanal vessels advised to avoid Zone A sector (12.95°N, 74.80°E).',
          action_advice: 'Issue NAVTEX broadcast to local fisheries federations.',
        },
        key_recommendations: [
          'Patrol western boundary near Zone A (14.5 NM WNW).',
          'Advise artisanal craft to utilize certified Zone B corridor.',
        ],
        evidence_summary: [
          'Station MB-04 reports significant wave height peak 2.7m and wind 24 kts at Zone A.',
        ],
        visual_payload: {
          focus_zone_id: 'ZONE_A',
          highlight_layer: 'restrictions',
          metric_badges: {
            'High Risk Zone': 'Zone A (75.2)',
            'Max Wave': '2.7 m (Zone A)',
            'Zone B Status': 'Safe (34.9)',
          },
        },
        status: 'success',
        execution_time_seconds: 0.29,
      };
    }

    if (normalized.includes('restricted') || normalized.includes('marine protected') || normalized.includes('sanctuary')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'maritime_operator',
        markdown_content:
          '**Restricted Maritime Areas Status: 1 Active Sanctuary, 0 Incursions**\n\n• **Mulki Marine Ecological Reserve (MPA-KA-04)**: Strict no-take zone under Wildlife Protection Act. Zone C falls directly inside reserve boundary.',
        safety_alert: {
          severity: 'caution_yellow',
          title: 'Ecological Sanctuary Enforced',
          description: 'Commercial trawling and motorized fishing strictly prohibited within polygon.',
          action_advice: 'Automated AIS geofence active; alert triggered if vessels enter at speed < 3 kts.',
        },
        key_recommendations: [
          'Zone C coordinates (12.82°N, 75.05°E) fall directly within Mulki MPA boundary.',
          'Commercial fishers steered to Zone B via automated mobile advisory.',
        ],
        evidence_summary: ['Boundary verified against Department of Fisheries Gazette Notification.'],
        visual_payload: {
          focus_zone_id: 'ZONE_C',
          highlight_layer: 'restrictions',
          metric_badges: {
            'Restricted Zones': 'Mulki MPA (Zone C)',
            Status: 'Strictly Enforced',
            Enforcement: 'ICG Patrol 102',
          },
        },
        status: 'success',
        execution_time_seconds: 0.26,
      };
    }

    if (normalized.includes('vessel') || normalized.includes('fleet') || normalized.includes('activity')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'maritime_operator',
        markdown_content:
          '**Coastal Fleet Activity Surveillance:**\n\n• Total Tracked Vessels: 22 crafts\n• Mechanized Trawlers: 14 vessels (concentrated near Zone B)\n• Artisanal Boats: 6 vessels in inshore waters (< 12m depth)\n• Coast Guard Patrol: 2 interceptors active (ICG Interceptor C-421, Coastal Security Police KP-08)',
        key_recommendations: [
          'Fleet distribution is well-clustered around recommended Zone B (8.2 NM SSW).',
          'Zero unauthorized incursions inside Mulki Marine Sanctuary (Zone C) in last 12 hours.',
        ],
        evidence_summary: ['Synthesized from coastal AIS transponders and VMS satellite telemetry.'],
        visual_payload: {
          highlight_layer: 'vessels',
          metric_badges: {
            'Total Vessels': '22 Tracked',
            'Fleet Mode': 'Normal Dispersal',
            'Near Sanctuary': '0 Incursions',
          },
        },
        status: 'success',
        execution_time_seconds: 0.27,
      };
    }
  }

  // ==========================================
  // 3. RESEARCHER PERSONA RESPONSES
  // ==========================================
  if (role === 'researcher') {
    if (normalized.includes('why is pfz') || normalized.includes('pfz strength') || normalized.includes('chlorophyll')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'researcher',
        markdown_content:
          '**Oceanographic Analysis: PFZ Front Formation Mechanisms**\n\nThe elevated PFZ strength along the Netravati ridge (Zone B) is driven by bathymetric upwelling at the 35-meter shelf break. Subsurface nutrient-rich colder waters encounter warm coastal currents, generating a 0.6°C horizontal SST gradient and sustained chlorophyll-a blooms (2.3 mg/m³).',
        key_recommendations: [
          'High correlation between MODIS Aqua chlorophyll concentration and pelagic school acoustic signatures.',
          'Recommended for multi-spectral time-series tracking over the next 48 hours.',
        ],
        evidence_summary: [
          'INCOIS PFZ Composite: Thermal Front persistence score 0.88.',
          'Chlorophyll-a anomaly: 2.3 mg/m³ across the 35m bathymetric contour.',
          'Ekman transport index indicates moderate offshore drift supporting nutrient retention.',
        ],
        visual_payload: {
          focus_zone_id: 'ZONE_B',
          highlight_layer: 'pfz',
          metric_badges: {
            'SST Delta': '0.6°C Front',
            Chlorophyll: '2.3 mg/m³',
            Confidence: '92% (High)',
            Depth: '35 m Shelf',
          },
        },
        status: 'success',
        execution_time_seconds: 0.32,
      };
    }

    if (normalized.includes('compare') || normalized.includes('zone a and zone b')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'researcher',
        markdown_content:
          '**Biophysical Comparison: Zone A vs. Zone B**\n\n| Variable | Zone A (Gurupura) | Zone B (Netravati) |\n| :--- | :--- | :--- |\n| **Opportunity Score** | 76.6 / 100 | 66.9 / 100 |\n| **Risk Score** | 75.2 / 100 (Hazard) | 34.9 / 100 (Safe) |\n| **Ranking Score** | Disqualified | **67.31 / 100** |\n| **Wave Height (Hs)** | 2.7 m (Rough) | 1.1 m (Slight) |\n| **Wind Speed** | 24 kts | 11 kts |\n| **Current Velocity** | 1.8 m/s | 0.8 m/s |\n| **SST Front** | 1.1°C delta | 0.6°C delta |\n| **Chlorophyll-a** | 2.8 mg/m³ | 2.3 mg/m³ |\n| **Legal Status** | Allowed | Allowed |\n| **Recommendation** | **DISQUALIFIED (Risk > 50)** | **OPTIMAL CANDIDATE** |',
        key_recommendations: [
          'Zone A exhibits high primary productivity (76.6) but fails hydrodynamic safety criteria (Risk 75.2 > 50).',
          'Zone B represents the optimal Pareto frontier between yield and vessel risk (Rank 67.31).',
        ],
        evidence_summary: [
          'P6 Deterministic Decision Engine: Safety threshold constraint (<= 50) overrides opportunity maximization.',
        ],
        visual_payload: {
          highlight_layer: 'zones',
          metric_badges: {
            'Selected Zone': 'Zone B (67.31)',
            'Zone A Risk': '75.2 (Hs = 2.7m)',
            'Zone B Risk': '34.9 (Hs = 1.1m)',
          },
        },
        status: 'success',
        execution_time_seconds: 0.35,
      };
    }

    if (normalized.includes('sst') || normalized.includes('trend') || normalized.includes('history')) {
      return {
        response_id: `resp_${Date.now()}`,
        role: 'researcher',
        markdown_content:
          '**SST Trends & Time-Series (Mangalore Shelf Sector):**\n\n• Baseline Coastal SST: 29.4°C\n• Zone B SST: 28.7°C (Thermal gradient: 0.6°C delta along 35m contour)\n• Zone A SST: 28.1°C (Thermal gradient: 1.1°C delta)\n• Upwelling Front: Active chlorophyll front (2.3 mg/m³)',
        key_recommendations: [
          'Upwelling event is entering peak stabilization phase along 35m contour.',
          'Expected to sustain pelagic feeding grounds for 3-4 days.',
        ],
        evidence_summary: [
          'Satellite IR sensor calibration: bias ±0.2°C against moored oceanographic buoys.',
        ],
        visual_payload: {
          highlight_layer: 'pfz',
          metric_badges: {
            'Zone B SST': '28.7°C',
            'SST Delta': '0.6°C',
            Chlorophyll: '2.3 mg/m³',
          },
        },
        status: 'success',
        execution_time_seconds: 0.31,
      };
    }
  }

  // Fallback response for unmapped general queries
  return {
    response_id: `resp_${Date.now()}`,
    role,
    markdown_content: `**Varidhi Intelligence Advisory**\n\nProcessed query: "${query}" across marine weather, INCOIS PFZ telemetry, and maritime safety databases.\n\nCurrent status for Mangalore coastal sector: Normal coastal conditions with active recommended fishing grounds at Zone B (8.2 NM SSW).`,
    key_recommendations: [
      'Zone B remains the primary recommendation for morning fishing trips.',
      'Check marine weather before venturing beyond 20 nautical miles.',
    ],
    evidence_summary: ['Synthesized across IMD, INCOIS PFZ and local bathymetry layers.'],
    visual_payload: {
      focus_zone_id: 'ZONE_B',
      highlight_layer: 'zones',
      metric_badges: {
        Status: 'Active',
        Location: 'Mangalore Sector',
      },
    },
    status: 'success',
    execution_time_seconds: 0.2,
  };
  */
}

export const FISHERMAN_QUICK_PROMPTS: QuickPrompt[] = [
  {
    id: 'p1',
    label: 'Best Fishing Zone',
    query: 'Where should I fish tomorrow morning?',
    category: 'advisory',
  },
  {
    id: 'p2',
    label: 'Is It Safe?',
    query: 'Is it safe to go tomorrow?',
    category: 'safety',
  },
  {
    id: 'p3',
    label: 'Why Zone B?',
    query: 'Why is Zone B recommended?',
    category: 'advisory',
  },
  {
    id: 'p4',
    label: 'Sea Conditions',
    query: 'What are the current sea conditions?',
    category: 'safety',
  },
];

export const AUTHORITY_QUICK_PROMPTS: QuickPrompt[] = [
  {
    id: 'a1',
    label: 'High-Risk Areas',
    query: 'Show high-risk areas near Mangalore.',
    category: 'monitoring',
  },
  {
    id: 'a2',
    label: 'Restricted Zones',
    query: 'Which fishing zones are currently restricted?',
    category: 'monitoring',
  },
  {
    id: 'a3',
    label: 'Fleet & Vessel Activity',
    query: 'Show vessel activity near the restricted zone.',
    category: 'monitoring',
  },
  {
    id: 'a4',
    label: 'Marine Hazards',
    query: 'Are there any major marine hazards today?',
    category: 'safety',
  },
];

export const RESEARCHER_QUICK_PROMPTS: QuickPrompt[] = [
  {
    id: 'r1',
    label: 'Why PFZ Strength High?',
    query: 'Why is PFZ strength high here?',
    category: 'analytics',
  },
  {
    id: 'r2',
    label: 'Compare Zone A vs B',
    query: 'Compare Zone A and Zone B.',
    category: 'analytics',
  },
  {
    id: 'r3',
    label: 'SST 7-Day Trend',
    query: 'Show SST trends over the last 7 days.',
    category: 'analytics',
  },
  {
    id: 'r4',
    label: 'Chlorophyll Bloom',
    query: 'Where did chlorophyll increase?',
    category: 'analytics',
  },
];
