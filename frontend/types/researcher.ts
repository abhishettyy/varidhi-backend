export interface TimeSeriesPoint {
  timestamp: string;
  sst: number;
  chlorophyll: number;
  pfzConfidence: number;
  waveHeight: number;
}

export interface OceanVariableComparison {
  zoneCode: string;
  sst: number;
  sstDelta: number;
  chlorophyll: number;
  bathymetryDepth: number;
  thermalFrontConvergence: boolean;
  opportunityScore: number;
  safetyScore: number;
}
