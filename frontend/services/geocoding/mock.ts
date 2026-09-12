import { GeocodingResult, GeocodingService } from './types';

const KNOWN_COASTAL_LOCATIONS: GeocodingResult[] = [
  {
    display_name: "Mangalore (Old Port Bunder), Karnataka, India",
    short_name: "Mangalore",
    latitude: 12.8550,
    longitude: 74.8360,
    state: "Karnataka",
    country: "India",
    is_port: true,
  },
  {
    display_name: "Malpe Fishing Harbour, Udupi, Karnataka, India",
    short_name: "Malpe",
    latitude: 13.3512,
    longitude: 74.7011,
    state: "Karnataka",
    country: "India",
    is_port: true,
  },
  {
    display_name: "Karwar Port (Baithkol), Uttara Kannada, Karnataka, India",
    short_name: "Karwar",
    latitude: 14.8136,
    longitude: 74.1240,
    state: "Karnataka",
    country: "India",
    is_port: true,
  },
  {
    display_name: "Kochi Marine Fisheries Harbour (Thoppumpady), Kerala, India",
    short_name: "Kochi",
    latitude: 9.9312,
    longitude: 76.2673,
    state: "Kerala",
    country: "India",
    is_port: true,
  },
  {
    display_name: "Sasoon Docks, Mumbai, Maharashtra, India",
    short_name: "Mumbai",
    latitude: 18.9167,
    longitude: 72.8258,
    state: "Maharashtra",
    country: "India",
    is_port: true,
  },
  {
    display_name: "Kasimedu Fishing Harbour, Chennai, Tamil Nadu, India",
    short_name: "Chennai",
    latitude: 13.1250,
    longitude: 80.2974,
    state: "Tamil Nadu",
    country: "India",
    is_port: true,
  },
  {
    display_name: "Visakhapatnam Fishing Harbour, Andhra Pradesh, India",
    short_name: "Visakhapatnam",
    latitude: 17.6868,
    longitude: 83.3013,
    state: "Andhra Pradesh",
    country: "India",
    is_port: true,
  },
];

export class MockGeocodingService implements GeocodingService {
  async searchLocation(query: string): Promise<GeocodingResult | null> {
    const cleanQuery = query.trim().toLowerCase();
    if (!cleanQuery) return null;

    // Exact or partial match on short name or display name
    const match = KNOWN_COASTAL_LOCATIONS.find(loc => 
      loc.short_name.toLowerCase().includes(cleanQuery) ||
      loc.display_name.toLowerCase().includes(cleanQuery)
    );

    return match || null;
  }

  async suggestLocations(query: string): Promise<GeocodingResult[]> {
    const cleanQuery = query.trim().toLowerCase();
    if (!cleanQuery) return KNOWN_COASTAL_LOCATIONS.slice(0, 5);

    return KNOWN_COASTAL_LOCATIONS.filter(loc =>
      loc.short_name.toLowerCase().includes(cleanQuery) ||
      loc.display_name.toLowerCase().includes(cleanQuery)
    );
  }

  getAllKnownLocations(): GeocodingResult[] {
    return [...KNOWN_COASTAL_LOCATIONS];
  }
}
