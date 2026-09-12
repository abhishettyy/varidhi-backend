import { SafetySeverity } from './marine';

export interface RegionalKPIs {
  activeAlertsCount: number;
  highRiskAreasCount: number;
  restrictedAreasCount: number;
  fishingFleetActivity: 'Low' | 'Moderate' | 'High' | 'Surge';
  weatherStatus: 'Stable' | 'Caution' | 'Advisory' | 'Severe';
  patrolCraftActive: number;
}

export interface AuthorityAlert {
  id: string;
  title: string;
  category: 'weather' | 'incursion' | 'cyclone' | 'gear_conflict';
  severity: SafetySeverity;
  region: string;
  description: string;
  issuedAt: string;
  affectedCoordinates?: [number, number];
  suggestedAction: string;
}

export interface FleetActivitySummary {
  totalVessels: number;
  mechanizedTrawlers: number;
  artisanalBoats: number;
  patrolInterceptors: number;
  vesselsNearSanctuary: number;
}
