"""P4 data adapters backed by the P5 data API.

This is where P4 talks to P5. Each fetch_* call:
  1. turns P4 tool parameters (location, planner time range, temporal mode)
     into a P5Query — relative phrases like "tomorrow morning" become an
     absolute time here, P5 only ever sees ISO timestamps;
  2. asks the active P5DataSource (in-process mock, HTTP service, or a live
     source later) for normalized records;
  3. reshapes them into the canonical ToolResult P3/P6 already consume.

The data keys match the synthetic adapters (zone_data, zone_wind,
zone_gradients, zones[].confidence, ...) so nothing downstream changes;
contract field names travel alongside them. Missing values stay None and are
reported through status/partial/missing_dependencies — never filled in.

Switch on with backend.agents.tools.registry_bridge.use_p5_tools().
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from backend.agents.tools.adapters.base import BaseDataAdapter
from backend.p5.source import (
    DEFAULT_RADIUS_NM, P5DataSource, P5Query, P5Response, format_time, get_p5_source, haversine_nm, parse_time,
)

IST = timezone(timedelta(hours=5, minutes=30))  # "tomorrow morning" means local morning on the coast
PERIOD_HOUR = {"morning": 6, "afternoon": 14, "evening": 18, "night": 21}
DAY_OFFSET = {"today": 0, "tomorrow": 1, "next 24 hours": 0, "next 48 hours": 0,
              "this week": 0, "this weekend": 0, "next week": 7}
HISTORY_DAYS = {"yesterday": 1, "last 7 days": 7, "last 30 days": 30, "past month": 30, "last month": 30, "last year": 365}
DEFAULT_HISTORY_DAYS = 30
QUALITY_RANK = {"high": 0, "moderate": 1, "degraded": 2, "missing": 3}
CARDINALS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


# ------------------------------------------------------------------ helpers
def _as_dict(value: Any) -> Dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return dict(vars(value))


def _place(location: Dict[str, Any], default: str = "Coastal Waters") -> str:
    lat, lon = location.get("latitude"), location.get("longitude")
    return location.get("name") or (f"({lat:.2f}, {lon:.2f})" if lat is not None and lon is not None else default)


def _latlon(rec: Dict[str, Any]) -> Tuple[float, float]:
    return rec["location"]["latitude"], rec["location"]["longitude"]


def _mean(values: Iterable[Optional[float]], digits: int) -> Optional[float]:
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), digits) if vals else None


def _circular_mean(degrees: Iterable[Optional[float]]) -> Optional[float]:
    """Directions average as vectors — the plain mean of 350° and 10° is 180°, i.e. backwards."""
    degs = [math.radians(d) for d in degrees if d is not None]
    if not degs:
        return None
    return round(math.degrees(math.atan2(sum(map(math.sin, degs)), sum(map(math.cos, degs)))) % 360, 1)


def _cardinal(deg: Optional[float]) -> Optional[str]:
    return None if deg is None else CARDINALS[round((deg % 360) / 22.5) % 16]


def _nearest(records: List[Dict[str, Any]], location: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not records:
        return None
    lat, lon = location.get("latitude"), location.get("longitude")
    if lat is None or lon is None:
        return records[0]
    return min(records, key=lambda r: haversine_nm(lat, lon, *_latlon(r)))


def _most_common(records: List[Dict[str, Any]], key: str) -> Optional[str]:
    values = [r[key] for r in records if r.get(key)]
    return Counter(values).most_common(1)[0][0] if values else None


# -------------------------------------------------------------- base class
class P5BackedAdapter(BaseDataAdapter):
    """Shared P4 <-> P5 plumbing: time resolution, querying, ToolResult envelope."""

    def __init__(self, source: Optional[P5DataSource] = None):
        self._source = source
        self._describe_cache: Dict[int, Dict[str, Any]] = {}

    @property
    def source(self) -> P5DataSource:
        return self._source or get_p5_source()

    def _describe(self) -> Dict[str, Any]:
        src = self.source
        if id(src) not in self._describe_cache:
            self._describe_cache[id(src)] = src.describe()
        return self._describe_cache[id(src)]

    @property
    def is_synthetic(self) -> bool:
        try:
            return bool(self._describe().get("synthetic"))
        except Exception:  # P5 unreachable: don't claim anything
            return False

    @property
    def source_name(self) -> str:
        return "synthetic" if self.is_synthetic else "p5"

    # ---- time
    def _anchor(self) -> datetime:
        """'Now' for relative phrases: a frozen mock dataset's reference time, else the wall clock."""
        d = self._describe()
        if d.get("synthetic") and d.get("reference_time"):
            return parse_time(d["reference_time"])  # type: ignore[return-value]
        return datetime.now(timezone.utc)

    def resolve_at(self, requested_time: Any) -> Optional[str]:
        """Planner time range -> absolute ISO time for P5. None means 'the source's now'."""
        rt = _as_dict(requested_time)
        for key in ("iso_start", "start", "at", "iso"):
            if rt.get(key):
                return str(rt[key])
        offset, hour = DAY_OFFSET.get(rt.get("relative_day")), PERIOD_HOUR.get(rt.get("period"))
        if offset is None or (offset == 0 and hour is None):
            return None
        local = self._anchor().astimezone(IST) + timedelta(days=offset)
        return format_time(local.replace(hour=6 if hour is None else hour, minute=0, second=0, microsecond=0))

    def resolve_window(self, requested_time: Any) -> Tuple[Optional[str], Optional[str]]:
        """Planner time range -> (start, end) for a historical series. (None, None) = everything."""
        rt = _as_dict(requested_time)
        start, end = rt.get("iso_start") or rt.get("start"), rt.get("iso_end") or rt.get("end")
        if end or (start and rt.get("is_historical")):
            return start, end
        if start:  # a single point in time: the history leading up to it
            t = parse_time(start)
            return format_time(t - timedelta(days=DEFAULT_HISTORY_DAYS)), format_time(t)  # type: ignore[operator]
        days = HISTORY_DAYS.get(rt.get("relative_day") or rt.get("raw"))
        if not days:
            return None, None
        anchor = self._anchor()
        return format_time(anchor - timedelta(days=days)), format_time(anchor)

    # ---- P5 call + envelope
    def _query(self, record_type: str, location: Dict[str, Any], **kw: Any) -> P5Response:
        return self.source.query(record_type, P5Query(
            latitude=location.get("latitude"), longitude=location.get("longitude"),
            radius_nm=float(location.get("radius_nm") or DEFAULT_RADIUS_NM), **kw,
        ))

    def _envelope(self, operation: str, resp: P5Response, data: Dict[str, Any], *,
                  observation_time: Optional[str] = None, valid_time: Optional[str] = None) -> Dict[str, Any]:
        qualities = [r.get("quality") or "high" for r in resp.records]
        res: Dict[str, Any] = {
            "status": resp.status,
            "source": self.source_name,
            "operation": operation,
            "observation_time": observation_time,
            "valid_time": valid_time,
            "data": data,
            "quality": max(qualities, key=lambda q: QUALITY_RANK.get(q, 0)) if qualities else "unavailable",
            "metadata": {
                "source_type": "p5",
                "p5_source": resp.metadata.get("source"),
                "contract_version": resp.metadata.get("contract_version"),
                "synthetic": resp.metadata.get("synthetic", False),
                "datasets": sorted({r["metadata"]["dataset"] for r in resp.records if r["metadata"].get("dataset")}),
                "upstream_equivalent": sorted({r["metadata"]["upstream_equivalent"] for r in resp.records
                                               if r["metadata"].get("upstream_equivalent")}),
                "p5_query": resp.query,
                "selection": resp.metadata.get("selection", []),
            },
        }
        if resp.status != "success":
            res["partial"] = resp.status == "partial"
        if resp.missing:
            res["missing_dependencies"] = [
                ":".join(str(p) for p in (m["zone_id"], m.get("variable"), m["reason"]) if p) for m in resp.missing
            ]
        if resp.status == "unavailable":
            reasons = sorted({m["reason"] for m in resp.missing}) or ["no_zones_in_area"]
            res["error"] = f"P5 has no {resp.record_type} data for this area/time ({', '.join(reasons)})"
        return res

    @staticmethod
    def _area(location: Dict[str, Any], key: str = "location") -> Dict[str, Any]:
        return {key: _place(location), "latitude": location.get("latitude"), "longitude": location.get("longitude")}


# -------------------------------------------------------------------- PFZ
class P5PFZAdapter(P5BackedAdapter):
    def fetch_pfz(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                  temporal_mode: str = "latest_available") -> Dict[str, Any]:
        resp = self._query("pfz", location, at=self.resolve_at(requested_time))
        zones = []
        for r in resp.records:
            d = r["data"]
            zones.append({
                "zone_id": d["zone_id"], "lat": d["latitude"], "lon": d["longitude"],
                "latitude": d["latitude"], "longitude": d["longitude"],
                "bearing": _cardinal(d["bearing_deg"]), "bearing_deg": d["bearing_deg"],
                "distance_nm": d["distance_nm"], "depth_m": d.get("depth_m"), "species": d["species"],
                "confidence": d["pfz_confidence"], "pfz_confidence": d["pfz_confidence"],
                "observation_time": r["observation_time"],
                "geometry": {"type": "Point", "coordinates": [d["longitude"], d["latitude"]]},
            })
        confs = [z["confidence"] for z in zones if z["confidence"] is not None]
        data = {**self._area(location, "region"), "zones": zones, "zone_count": len(zones),
                "confidence": max(confs) if confs else None, "temporal_mode": temporal_mode,
                "distance_reference": "distance_nm/bearing are from the dataset's reference harbour"}
        obs = max((r["observation_time"] for r in resp.records), default=None)
        return self._envelope("get_pfz", resp, data, observation_time=obs)


# ---------------------------------------------------------- SST / Chl-a / history
class P5OceanAdapter(P5BackedAdapter):
    def fetch_sst(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                  temporal_mode: str = "latest_available") -> Dict[str, Any]:
        resp = self._query("sst", location, at=self.resolve_at(requested_time))
        zone_gradients, zone_data = {}, {}
        for r in resp.records:
            d = r["data"]
            common = {"latitude": d["latitude"], "longitude": d["longitude"], "sst_celsius": d["sst_celsius"], "unit": "degC",
                      "gradient_celsius_per_km": d["gradient_celsius_per_km"],
                      "thermal_front_delta_celsius": d["thermal_front_delta_celsius"],
                      "observation_time": r["observation_time"], "quality": r["quality"]}
            zone_gradients[d["zone_id"]] = {**common, "gradient": d["thermal_front_delta_celsius"]}
            zone_data[d["zone_id"]] = {"zone_id": d["zone_id"], **common, "gradient_delta": d["thermal_front_delta_celsius"]}
        mean_sst = _mean((z["sst_celsius"] for z in zone_data.values()), 2)
        data = {**self._area(location), "value": mean_sst, "mean_sst_celsius": mean_sst, "unit": "degC",
                "gradient_celsius_per_km": _mean((z["gradient_celsius_per_km"] for z in zone_data.values()), 3),
                "zone_gradients": zone_gradients, "zone_data": zone_data, "temporal_mode": temporal_mode}
        obs = max((r["observation_time"] for r in resp.records), default=None)
        return self._envelope("get_sst", resp, data, observation_time=obs)

    def fetch_chlorophyll(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                          temporal_mode: str = "latest_available") -> Dict[str, Any]:
        resp = self._query("chlorophyll", location, at=self.resolve_at(requested_time))
        zone_chl, zone_data = {}, {}
        for r in resp.records:
            d = r["data"]
            common = {"latitude": d["latitude"], "longitude": d["longitude"], "unit": "mg/m3",
                      "chlorophyll_a_mg_m3": d["chlorophyll_a_mg_m3"], "observation_time": r["observation_time"]}
            zone_chl[d["zone_id"]] = {**common, "chla_mg_m3": d["chlorophyll_a_mg_m3"]}
            zone_data[d["zone_id"]] = {"zone_id": d["zone_id"], **common, "quality": r["quality"]}
        mean_chl = _mean((z["chlorophyll_a_mg_m3"] for z in zone_data.values()), 3)
        data = {**self._area(location), "value": mean_chl, "chlorophyll_a_mg_m3": mean_chl, "unit": "mg/m3",
                "zone_chlorophyll": zone_chl, "zone_data": zone_data, "temporal_mode": temporal_mode}
        obs = max((r["observation_time"] for r in resp.records), default=None)
        return self._envelope("get_chlorophyll", resp, data, observation_time=obs)

    def fetch_historical(self, location: Dict[str, Any], variable: str = "SST",
                         requested_time: Optional[Dict[str, Any]] = None, zone_id: Optional[str] = None) -> Dict[str, Any]:
        start, end = self.resolve_window(requested_time)
        resp = self._query("historical", location, variable=variable, start=start, end=end,
                           zone_ids=[zone_id] if zone_id else None)
        zone_series = {
            r["zone_id"]: {"variable": r["data"]["variable"], "unit": r["data"]["unit"], "series": r["data"]["series"],
                           "points": r["metadata"]["points"], "missing_points": r["metadata"]["missing_points"]}
            for r in resp.records
        }
        nearest = _nearest(resp.records, location)
        primary = zone_id if zone_id in zone_series else (nearest["zone_id"] if nearest else None)
        series = zone_series[primary]["series"] if primary else []
        data = {**self._area(location), "variable": variable.upper(),
                "unit": zone_series[primary]["unit"] if primary else None, "zone_id": primary, "series": series,
                "time_series": [{"date": p["timestamp"][:10], "value": p["value"]} for p in series],  # legacy mock shape
                "record_count": len(series), "zone_series": zone_series, "temporal_mode": "historical"}
        return self._envelope("get_historical_data", resp, data, observation_time=series[-1]["timestamp"] if series else None)


# ------------------------------------------------ wind / wave / swell / tide / currents
class P5MarineWeatherAdapter(P5BackedAdapter):
    def _forecast(self, record_type: str, location: Dict[str, Any], requested_time: Any) -> P5Response:
        return self._query(record_type, location, at=self.resolve_at(requested_time))

    def _forecast_envelope(self, operation: str, resp: P5Response, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self._envelope(operation, resp, data, valid_time=_most_common(resp.records, "valid_time"))
        if resp.records:
            res["metadata"]["model_run_time"] = resp.records[0]["metadata"].get("model_run_time")
        return res

    def fetch_wind(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                   temporal_mode: str = "forecast") -> Dict[str, Any]:
        resp = self._forecast("wind", location, requested_time)
        zone_wind, zone_data = {}, {}
        for r in resp.records:
            d, (lat, lon) = r["data"], _latlon(r)
            legacy = {"speed_knots": d["wind_speed_knots"], "gust_knots": d["gust_knots"],
                      "direction_deg": d["wind_direction_deg"], "direction_cardinal": d["wind_direction"]}
            contract = {k: d[k] for k in ("wind_speed_knots", "wind_speed_ms", "wind_direction_deg", "wind_direction")}
            zone_wind[d["zone_id"]] = {"latitude": lat, "longitude": lon, **legacy, **contract}
            zone_data[d["zone_id"]] = {"zone_id": d["zone_id"], "latitude": lat, "longitude": lon, **legacy, **contract,
                                       "unit": "knots", "valid_time": r["valid_time"], "quality": r["quality"]}
        speed = _mean((z["speed_knots"] for z in zone_data.values()), 1)
        direction = _circular_mean(z["direction_deg"] for z in zone_data.values())
        data = {**self._area(location), "speed_knots": speed, "wind_speed_knots": speed,
                "speed_ms": None if speed is None else round(speed * 0.514444, 2),
                "gust_knots": _mean((z["gust_knots"] for z in zone_data.values()), 1),
                "direction_deg": direction, "direction_cardinal": _cardinal(direction), "unit": "knots",
                "zone_wind": zone_wind, "zone_data": zone_data, "temporal_mode": temporal_mode}
        return self._forecast_envelope("get_wind", resp, data)

    def fetch_wave(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                   temporal_mode: str = "forecast") -> Dict[str, Any]:
        resp = self._forecast("wave", location, requested_time)
        zone_wave, zone_data = {}, {}
        for r in resp.records:
            d, (lat, lon) = r["data"], _latlon(r)
            vals = {"significant_wave_height_m": d["significant_wave_height_m"], "wave_height_m": d["significant_wave_height_m"],
                    "wave_period_s": d["wave_period_s"], "wave_period_sec": d["wave_period_s"],
                    "wave_direction_deg": d["wave_direction_deg"]}
            zone_wave[d["zone_id"]] = {"latitude": lat, "longitude": lon, **vals}
            zone_data[d["zone_id"]] = {"zone_id": d["zone_id"], "latitude": lat, "longitude": lon, **vals, "unit": "m",
                                       "valid_time": r["valid_time"], "quality": r["quality"]}
        period = _mean((z["wave_period_s"] for z in zone_data.values()), 1)
        data = {**self._area(location),
                "significant_wave_height_m": _mean((z["significant_wave_height_m"] for z in zone_data.values()), 2),
                "wave_period_s": period, "wave_period_sec": period,
                "wave_direction_deg": _circular_mean(z["wave_direction_deg"] for z in zone_data.values()), "unit": "m",
                "zone_wave": zone_wave, "zone_data": zone_data, "temporal_mode": temporal_mode}
        return self._forecast_envelope("get_wave", resp, data)

    def fetch_swell(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                    temporal_mode: str = "forecast") -> Dict[str, Any]:
        resp = self._forecast("swell", location, requested_time)
        zone_swell = {}
        for r in resp.records:
            d, (lat, lon) = r["data"], _latlon(r)
            zone_swell[d["zone_id"]] = {"latitude": lat, "longitude": lon, "swell_height_m": d["swell_height_m"],
                                        "swell_period_s": d["swell_period_s"], "swell_period_sec": d["swell_period_s"],
                                        "swell_direction_deg": d["swell_direction_deg"], "valid_time": r["valid_time"]}
        period = _mean((z["swell_period_s"] for z in zone_swell.values()), 1)
        data = {**self._area(location), "swell_height_m": _mean((z["swell_height_m"] for z in zone_swell.values()), 2),
                "swell_period_s": period, "swell_period_sec": period,
                "swell_direction_deg": _circular_mean(z["swell_direction_deg"] for z in zone_swell.values()),
                "unit": "m", "zone_swell": zone_swell, "temporal_mode": temporal_mode}
        return self._forecast_envelope("get_swell", resp, data)

    def fetch_tide(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                   temporal_mode: str = "forecast") -> Dict[str, Any]:
        """Tide is a point quantity: report the zone nearest the requested location, plus every zone."""
        resp = self._forecast("tide", location, requested_time)
        zone_tide = {r["zone_id"]: {k: r["data"][k] for k in ("water_level_m", "tide_phase", "next_high_tide", "next_low_tide")}
                     for r in resp.records}
        near = _nearest(resp.records, location)
        d = near["data"] if near else {}
        data = {**self._area(location), "tide_phase": d.get("tide_phase"), "water_level_m": d.get("water_level_m"),
                "next_high_tide": d.get("next_high_tide"), "next_low_tide": d.get("next_low_tide"),
                "unit": "m", "datum": "chart_datum", "reference_zone_id": near["zone_id"] if near else None,
                "zone_tide": zone_tide, "temporal_mode": temporal_mode}
        return self._forecast_envelope("get_tide", resp, data)

    def fetch_currents(self, location: Dict[str, Any], requested_time: Optional[Dict[str, Any]] = None,
                       temporal_mode: str = "forecast") -> Dict[str, Any]:
        resp = self._forecast("currents", location, requested_time)
        zone_currents = {r["zone_id"]: {"current_speed_knots": r["data"]["current_speed_knots"],
                                        "current_direction_deg": r["data"]["current_direction_deg"]} for r in resp.records}
        near = _nearest(resp.records, location)
        d = near["data"] if near else {}
        data = {**self._area(location), "current_speed_knots": d.get("current_speed_knots"),
                "current_direction_deg": d.get("current_direction_deg"),
                "direction_convention": "towards", "unit": "knots",
                "reference_zone_id": near["zone_id"] if near else None, "zone_currents": zone_currents,
                "temporal_mode": temporal_mode}
        return self._forecast_envelope("get_currents", resp, data)


# ------------------------------------------------------------ restrictions
class P5RestrictionsAdapter(P5BackedAdapter):
    def check_restrictions(self, location: Dict[str, Any], vessel: Optional[Dict[str, Any]] = None,
                           requested_time: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self._query("restrictions", location, at=self.resolve_at(requested_time))
        zone_restrictions = {}
        for r in resp.records:
            d, (lat, lon) = r["data"], _latlon(r)
            zone_restrictions[d["zone_id"]] = {
                "zone_id": d["zone_id"], "latitude": lat, "longitude": lon, "restricted": d["restricted"],
                "status": d["regulatory_status"], "reason": d["restriction_reason"],
                "regulatory_status": d["regulatory_status"], "restriction_reason": d["restriction_reason"],
                "valid_from": d["valid_from"], "valid_until": d["valid_until"], "authority": d["source"],
            }
        data = {**self._area(location), "restricted": any(z["restricted"] for z in zone_restrictions.values()),
                "zone_restrictions": zone_restrictions, "active_regulatory_areas": [], "temporal_mode": "latest_available"}
        obs = max((r["observation_time"] for r in resp.records), default=None)
        return self._envelope("check_restrictions", resp, data, observation_time=obs)
