import { GeocodingService } from './types';
import { MockGeocodingService } from './mock';

// Default provider instance
const activeProvider: GeocodingService = new MockGeocodingService();

export function getGeocodingService(): GeocodingService {
  return activeProvider;
}

export async function geocodeLocation(query: string) {
  return activeProvider.searchLocation(query);
}

export async function getSuggestedLocations(query: string) {
  return activeProvider.suggestLocations(query);
}

export function getAllPorts() {
  return activeProvider.getAllKnownLocations();
}

export * from './types';
