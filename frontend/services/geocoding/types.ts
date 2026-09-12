export interface GeocodingResult {
  display_name: string;
  short_name: string;
  latitude: number;
  longitude: number;
  state?: string;
  country: string;
  is_port?: boolean;
}

export interface GeocodingService {
  searchLocation(query: string): Promise<GeocodingResult | null>;
  suggestLocations(query: string): Promise<GeocodingResult[]>;
  getAllKnownLocations(): GeocodingResult[];
}
