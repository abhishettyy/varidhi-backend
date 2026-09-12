import { FishingZone, UserLocation } from '@/types/marine';
import mangaloreZonesRaw from '@/data/mock/mangalore_zones.json';
import mangaloreLocationRaw from '@/data/mock/mangalore_location.json';
import mangalorePfzGeojson from '@/data/mock/mangalore_pfz.json';
import mangaloreRestrictionsGeojson from '@/data/mock/mangalore_restrictions.json';
import mangaloreWeatherGeojson from '@/data/mock/mangalore_weather.json';
import mangaloreVesselsGeojson from '@/data/mock/mangalore_vessels.json';
import mangaloreCycloneGeojson from '@/data/mock/mangalore_cyclone.json';

export function getMockZones(): FishingZone[] {
  return mangaloreZonesRaw as FishingZone[];
}

export function getMockUserLocation(): UserLocation {
  return mangaloreLocationRaw as UserLocation;
}

export function getMockPfzGeoJSON(): GeoJSON.FeatureCollection {
  return mangalorePfzGeojson as unknown as GeoJSON.FeatureCollection;
}

export function getMockRestrictionsGeoJSON(): GeoJSON.FeatureCollection {
  return mangaloreRestrictionsGeojson as unknown as GeoJSON.FeatureCollection;
}

export function getMockWeatherGeoJSON(): GeoJSON.FeatureCollection {
  return mangaloreWeatherGeojson as unknown as GeoJSON.FeatureCollection;
}

export function getMockVesselsGeoJSON(): GeoJSON.FeatureCollection {
  return mangaloreVesselsGeojson as unknown as GeoJSON.FeatureCollection;
}

export function getMockCycloneGeoJSON(): GeoJSON.FeatureCollection {
  return mangaloreCycloneGeojson as unknown as GeoJSON.FeatureCollection;
}
