import { FishingZone, SafetySeverity } from './marine';

export interface FishermanRecommendation {
  zone: FishingZone;
  distanceKm: number;
  bearing: string;
  opportunityRating: 'VERY HIGH' | 'HIGH' | 'MODERATE' | 'LOW';
  safetyRating: 'GOOD' | 'CAUTION' | 'DANGEROUS';
  legalStatus: 'ALLOWED' | 'RESTRICTED';
  keyReasons: string[];
  safetyAdvisory: string;
  recommendedDepartureTime: string;
  estimatedReturnTime: string;
}

export interface SeaConditionsSummary {
  windSpeedKmh: number;
  windHeading: string;
  waveHeightM: number;
  swellDirection: string;
  swellPeriodS: number;
  currentSpeedMs: number;
  sstCelsius: number;
  seaState: 'Calm' | 'Smooth' | 'Slight' | 'Moderate' | 'Rough' | 'Very Rough';
  safetyVerdict: 'GOOD TO GO' | 'EXERCISE CAUTION' | 'DO NOT VENTURE';
  safetySeverity: SafetySeverity;
}
