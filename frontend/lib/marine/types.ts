export type FieldKey = "waves" | "wind" | "currents" | "sst" | "chl";
export type MarkerKey = "pfz" | "risk" | "restricted" | "cyclone" | "vessels";

export interface LatLon {
  lat: number;
  lon: number;
}

/** One field reading. `u`/`w` are the unit east/north components of travel. */
export interface Sample {
  v: number;
  u: number;
  w: number;
  /** wave period in seconds, waves only */
  p?: number;
}
