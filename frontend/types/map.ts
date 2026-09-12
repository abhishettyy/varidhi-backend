export interface LayerVisibility {
  pfz: boolean;
  zones: boolean;
  restrictions: boolean;
  userLocation: boolean;
  // Future layer placeholders for extensibility
  sst: boolean;
  chlorophyll: boolean;
  weather: boolean;
  vessels: boolean;
  cyclone: boolean;
}

export interface MapViewport {
  latitude: number;
  longitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
}
