export interface GeocodingResult {
  display_name: string;
  short_name: string;
  latitude: number;
  longitude: number;
  state?: string;
  country: string;
  is_port?: boolean;
}
