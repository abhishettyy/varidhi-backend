export type RoleType = 'fisherman' | 'researcher' | 'maritime_operator' | 'general';

export type SafetySeverity = 'safe_green' | 'caution_yellow' | 'warning_orange' | 'danger_red';

export type RecommendationStatus = 'recommended' | 'alternative' | 'high_risk' | 'restricted';

export type LegalStatus = 'allowed' | 'restricted';

export interface FishingZone {
  id: string;
  name: string;
  code: string; // e.g. "ZONE B"
  status: RecommendationStatus;
  opportunity_score: number; // 0 - 100
  risk_score?: number;       // 0 - 100
  safety_score: number;      // 0 - 100
  ranking_score?: number;    // 0 - 100 (composite)
  distance_km: number;       // Distance from selected port/user location
  bearing: string;           // e.g. "SSW", "245°"
  target_depth_m: number;    // Bathymetry depth
  legal_status: LegalStatus;
  species: string[];         // Target species
  coordinates: [number, number]; // [longitude, latitude]
  reasons: string[];         // Decision engine reasons
  warnings?: string[];       // Marine safety warnings
  evidence: {
    pfz_source: string;
    sst_front: string;
    chlorophyll: string;
    weather_condition: string;
    restriction_check: string;
  };
}

export interface PFZProperties {
  id: string;
  confidence: number;
  source: string;
  valid_time: string;
  depth_m: number;
  sst_delta: string;
  target_species: string[];
}

export interface RestrictionProperties {
  id: string;
  name: string;
  restriction_type: 'marine_protected_area' | 'naval_exercise_zone' | 'coral_reef_sanctuary';
  authority: string;
  description: string;
  legal_notice: string;
}

export interface UserLocation {
  name: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
  is_default: boolean;
}
