"""P5 data access API — the single interface P4 uses to read P5 data.

P4 adapters never read files or upstream APIs themselves. They build a
`P5Query`, call `get_p5_source().query(record_type, query)` and get back a
`P5Response` of normalized P5 records (see generate_mock_dataset.py for the
record contract). What sits behind the interface is swappable:

    MockP5DataSource   reads the generated JSONL dataset in-process (default)
    HttpP5DataSource   calls the P5 HTTP service (backend/p5/api.py); chosen
                       automatically when the P5_API_URL environment variable is set
    <real P5 source>   later: live INCOIS / NOAA / Open-Meteo ingestion, same interface

Selection rules (P5 decides *which* record answers a question, never what it means):
  latest_available (pfz, sst, chlorophyll)
      newest observation at or before `at`, within LATEST_WINDOW_DAYS. If the
      newest one has no primary value (e.g. cloud-covered chlorophyll) the most
      recent valid one is used and the fallback is reported in metadata.selection.
  restrictions
      newest notice at or before `at`, with no look-back limit — a standing
      regulation (a sanctuary notified in January) is still in force today.
  forecast (wind, wave, swell, tide, currents)
      the forecast step whose valid_time is closest to `at`, within
      FORECAST_TOLERANCE. Outside the forecast horizon the zone is reported
      missing — values are never extrapolated.
  historical
      the daily series for `variable`, clipped to [start, end]. Raw points only.
"""

from __future__ import annotations

import copy
import json
import math
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Protocol, Tuple, runtime_checkable

RECORD_TYPES = ("pfz", "sst", "chlorophyll", "wind", "wave", "swell", "tide", "currents", "restrictions", "historical")
OBSERVATION_TYPES = frozenset({"pfz", "sst", "chlorophyll", "restrictions"})
FORECAST_TYPES = frozenset({"wind", "wave", "swell", "tide", "currents"})
PRIMARY_FIELD = {"pfz": "pfz_confidence", "sst": "sst_celsius", "chlorophyll": "chlorophyll_a_mg_m3"}

DEFAULT_RADIUS_NM = 60.0
LATEST_WINDOW_DAYS = 8
FORECAST_TOLERANCE = timedelta(hours=3)  # half the 6-hourly step
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "mock" / "p5"
DEFAULT_COMPLETE_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "p5_data.json"


class P5Error(ValueError):
    """The request itself is invalid (unknown record type, malformed time)."""


def parse_time(value: Optional[str]) -> Optional[datetime]:
    if value in (None, ""):
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as e:
        raise P5Error(f"invalid ISO 8601 time: {value!r}") from e
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def format_time(dt: Optional[datetime]) -> Optional[str]:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = math.radians
    a = math.sin(r(lat2 - lat1) / 2) ** 2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a)) / 1.852


# ------------------------------------------------------------ query/response
@dataclass
class P5Query:
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_nm: float = DEFAULT_RADIUS_NM
    zone_ids: Optional[List[str]] = None
    at: Optional[str] = None          # ISO 8601; default = the source's reference time
    start: Optional[str] = None       # historical window start
    end: Optional[str] = None         # historical window end
    variable: Optional[str] = None    # historical variable: SST, CHLOROPHYLL_A, WIND_SPEED, SIGNIFICANT_WAVE_HEIGHT

    # HTTP query-string names (also what P5Response.query echoes)
    def to_params(self) -> Dict[str, Any]:
        p = {"lat": self.latitude, "lon": self.longitude, "radius_nm": self.radius_nm, "zone_id": self.zone_ids,
             "at": self.at, "start": self.start, "end": self.end, "variable": self.variable}
        return {k: v for k, v in p.items() if v is not None}

    @classmethod
    def from_params(cls, p: Mapping[str, Any]) -> "P5Query":
        zone = p.get("zone_id")
        return cls(
            latitude=None if p.get("lat") is None else float(p["lat"]),
            longitude=None if p.get("lon") is None else float(p["lon"]),
            radius_nm=float(p.get("radius_nm", DEFAULT_RADIUS_NM)),
            zone_ids=[zone] if isinstance(zone, str) else (list(zone) if zone else None),
            at=p.get("at"), start=p.get("start"), end=p.get("end"), variable=p.get("variable"),
        )


@dataclass
class P5Response:
    status: str                       # success | partial | unavailable
    record_type: str
    records: List[Dict[str, Any]]     # normalized P5 records, untouched except historical clipping
    missing: List[Dict[str, Any]] = field(default_factory=list)   # [{"zone_id", "reason"}]
    query: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Mapping[str, Any]) -> "P5Response":
        return cls(status=d["status"], record_type=d["record_type"], records=list(d.get("records", [])),
                   missing=list(d.get("missing", [])), query=dict(d.get("query", {})), metadata=dict(d.get("metadata", {})))


@runtime_checkable
class P5DataSource(Protocol):
    """What every P5 backend (mock, HTTP client, live ingestion) must provide."""
    name: str

    def query(self, record_type: str, query: Optional[P5Query] = None) -> P5Response: ...

    def zones(self) -> List[Dict[str, Any]]: ...

    def describe(self) -> Dict[str, Any]: ...


# ------------------------------------------------------------- mock source
class MockP5DataSource:
    """Serves the checked-in normalized P5 dataset in-process."""

    name = "p5-mock"

    def __init__(self, data_dir: Optional[Path | str] = None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._manifest: Optional[Dict[str, Any]] = None

    # ---- loading
    @property
    def manifest(self) -> Dict[str, Any]:
        if self._manifest is None:
            path = self.data_dir / "manifest.json"
            if not path.exists():
                raise FileNotFoundError(f"P5 mock dataset not found at {self.data_dir} — run "
                                        "`python -m backend.p5.generate_mock_dataset` first")
            self._manifest = json.loads(path.read_text(encoding="utf-8"))
        return self._manifest

    @property
    def reference_time(self) -> datetime:
        return parse_time(self.manifest["reference_time"])  # type: ignore[return-value]

    def _records(self, rtype: str) -> List[Dict[str, Any]]:
        if rtype not in self._cache:
            with open(self.data_dir / f"{rtype}.jsonl", encoding="utf-8") as f:
                self._cache[rtype] = [json.loads(line) for line in f if line.strip()]
        return self._cache[rtype]

    def describe(self) -> Dict[str, Any]:
        m = self.manifest
        return {"source": self.name, "contract_version": m["contract_version"], "reference_time": m["reference_time"],
                "synthetic": m["synthetic"], "record_counts": m["record_counts"], "region": m["region"],
                "record_types": list(RECORD_TYPES),
                "dataset_files": [f"data/mock/p5/{record_type}.jsonl" for record_type in RECORD_TYPES
                                  if (self.data_dir / f"{record_type}.jsonl").exists()],
                "raw_dataset_files": [
                    "data/raw/waves/waves_mangalore_20230101.nc",
                ],
                "processed_dataset_directories": [
                    "data/processed/sst",
                    "data/processed/chlorophyll",
                    "data/processed/marine_forecast",
                ]}

    def zones(self) -> List[Dict[str, Any]]:
        return [dict(z) for z in self.manifest["zones"]]

    # ---- query
    def query(self, record_type: str, query: Optional[P5Query] = None) -> P5Response:
        if record_type not in RECORD_TYPES:
            raise P5Error(f"unknown record_type {record_type!r}; expected one of {', '.join(RECORD_TYPES)}")
        q = query or P5Query()
        at = parse_time(q.at) or self.reference_time
        zone_ids, missing = self._select_zones(q)
        by_zone: Dict[str, List[Dict[str, Any]]] = {z: [] for z in zone_ids}
        for r in self._records(record_type):
            if r["zone_id"] in by_zone:
                by_zone[r["zone_id"]].append(r)

        if record_type in FORECAST_TYPES:
            records, more, selection = self._pick_forecast(by_zone, at)
        elif record_type == "historical":
            records, more, selection = self._pick_historical(by_zone, q)
        else:
            records, more, selection = self._pick_latest(record_type, by_zone, at)
        missing += more

        degraded = any(r["quality"] in ("degraded", "missing") for r in records) or any(s.get("fallback_from") for s in selection)
        status = "unavailable" if not records else ("partial" if missing or degraded else "success")
        return P5Response(
            status=status, record_type=record_type, records=records, missing=missing,
            query={**q.to_params(), "resolved_at": format_time(at)},
            metadata={"source": self.name, "contract_version": self.manifest["contract_version"],
                      "reference_time": self.manifest["reference_time"], "synthetic": True, "selection": selection},
        )

    def _select_zones(self, q: P5Query) -> Tuple[List[str], List[Dict[str, Any]]]:
        known = {z["zone_id"]: z for z in self.manifest["zones"]}
        if q.zone_ids:
            chosen = [z for z in q.zone_ids if z in known]
            return chosen, [{"zone_id": z, "reason": "unknown_zone"} for z in q.zone_ids if z not in known]
        if q.latitude is not None and q.longitude is not None:
            chosen = [zid for zid, z in known.items()
                      if haversine_nm(q.latitude, q.longitude, z["latitude"], z["longitude"]) <= q.radius_nm]
            return chosen, []
        return list(known), []

    def _pick_latest(self, rtype: str, by_zone: Dict[str, List[Dict[str, Any]]], at: datetime):
        records, missing, selection = [], [], []
        primary = PRIMARY_FIELD.get(rtype)
        # Standing regulations never age out; satellite data does.
        oldest = None if rtype == "restrictions" else at - timedelta(days=LATEST_WINDOW_DAYS)

        def in_window(r: Dict[str, Any]) -> bool:
            t = parse_time(r["observation_time"])
            return t <= at and (oldest is None or t >= oldest)  # type: ignore[operator]

        for zid, recs in by_zone.items():
            window = sorted(filter(in_window, recs), key=lambda r: r["observation_time"], reverse=True)
            if not window:
                missing.append({"zone_id": zid, "reason": "no_observation_in_window"})
                continue
            chosen = next((r for r in window if primary is None or r["data"].get(primary) is not None), None)
            if chosen is None:
                missing.append({"zone_id": zid, "reason": window[0]["metadata"].get("missing_reason") or "no_valid_observation"})
                continue
            obs = parse_time(chosen["observation_time"])
            selection.append({
                "zone_id": zid, "observation_time": chosen["observation_time"],
                "age_hours": round((at - obs).total_seconds() / 3600, 1),  # type: ignore[operator]
                "fallback_from": window[0]["observation_time"] if chosen is not window[0] else None,
            })
            records.append(chosen)
        return records, missing, selection

    def _pick_forecast(self, by_zone: Dict[str, List[Dict[str, Any]]], at: datetime):
        records, missing, selection = [], [], []
        for zid, recs in by_zone.items():
            if not recs:
                missing.append({"zone_id": zid, "reason": "no_forecast"})
                continue
            best = min(recs, key=lambda r: abs(parse_time(r["valid_time"]) - at))  # type: ignore[operator]
            gap = abs(parse_time(best["valid_time"]) - at)  # type: ignore[operator]
            if gap > FORECAST_TOLERANCE:
                missing.append({"zone_id": zid, "reason": "outside_forecast_horizon"})
                continue
            selection.append({"zone_id": zid, "valid_time": best["valid_time"], "offset_hours": round(gap.total_seconds() / 3600, 1)})
            records.append(best)
        return records, missing, selection

    def _pick_historical(self, by_zone: Dict[str, List[Dict[str, Any]]], q: P5Query):
        records, missing, selection = [], [], []
        start, end = parse_time(q.start), parse_time(q.end)
        want = q.variable.upper() if q.variable else None
        for zid, recs in by_zone.items():
            matches = [r for r in recs if want is None or r["data"]["variable"] == want]
            if not matches:
                missing.append({"zone_id": zid, "reason": "unknown_variable" if want else "no_history"})
                continue
            for r in matches:
                pts = [p for p in r["data"]["series"]
                       if (start is None or parse_time(p["timestamp"]) >= start) and (end is None or parse_time(p["timestamp"]) <= end)]
                if not pts:
                    missing.append({"zone_id": zid, "variable": r["data"]["variable"], "reason": "no_points_in_window"})
                    continue
                clipped = copy.deepcopy(r)
                clipped["data"]["series"] = pts
                nulls = sum(1 for p in pts if p["value"] is None)
                clipped["metadata"].update(start=pts[0]["timestamp"], end=pts[-1]["timestamp"], points=len(pts), missing_points=nulls)
                clipped["observation_time"] = pts[-1]["timestamp"]
                clipped["quality"] = "degraded" if nulls else "high"
                records.append(clipped)
                selection.append({"zone_id": zid, "variable": r["data"]["variable"], "points": len(pts), "missing_points": nulls})
        return records, missing, selection


# ------------------------------------------------------- complete data source
class CompleteP5DataSource:
    """Serve wide, real-plus-enriched zone observations from ``p5_data.json``."""

    name = "p5-complete"
    FIELD_TYPES = {
        "sst": "sea_surface_temperature",
        "chlorophyll": "chlorophyll_a_mg_m3",
        "wind": "wind_speed",
        "wave": "significant_wave_height",
        "swell": "swell_height_m",
        "tide": "water_level_m",
        "currents": "current_speed_knots",
    }

    def __init__(self, path: Optional[Path | str] = None):
        self.path = Path(path) if path else DEFAULT_COMPLETE_DATA_PATH
        if not self.path.exists():
            raise FileNotFoundError(f"Complete P5 dataset not found at {self.path}")
        self._rows = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(self._rows, list):
            raise P5Error("complete P5 dataset must be a JSON array")

    def describe(self) -> Dict[str, Any]:
        times = [parse_time(row["valid_time"]) for row in self._rows]
        return {
            "source": self.name,
            "contract_version": "p5-complete-v1",
            "synthetic": False,
            "dataset_file": str(self.path),
            "reference_time": format_time(max(times)) if times else None,
            "record_types": sorted(self.FIELD_TYPES),
            "record_counts": {record_type: len(self._rows) for record_type in self.FIELD_TYPES},
            "region": {"name": "GRIB/Copernicus observation zones"},
        }

    def zones(self) -> List[Dict[str, Any]]:
        return [{"zone_id": row["zone_id"], "latitude": row["latitude"], "longitude": row["longitude"],
                 "golden_fixture": False, "regulatory_status": "UNKNOWN"} for row in self._rows]

    def _select_rows(self, query: P5Query) -> List[Dict[str, Any]]:
        rows = list(self._rows)
        if query.zone_ids:
            rows = [row for row in rows if row["zone_id"] in query.zone_ids]
        if query.latitude is not None and query.longitude is not None:
            rows = [row for row in rows if haversine_nm(query.latitude, query.longitude,
                row["latitude"], row["longitude"]) <= query.radius_nm]
        return rows

    def _record(self, row: Dict[str, Any], record_type: str) -> Optional[Dict[str, Any]]:
        field = self.FIELD_TYPES[record_type]
        if field not in row.get("data", {}):
            return None
        values = row["data"]
        common = {"record_id": f"{record_type}:{row['zone_id']}:{row['valid_time']}",
                  "record_type": record_type, "contract_version": "p5-complete-v1",
                  "zone_id": row["zone_id"],
                  "location": {"name": row["zone_id"], "latitude": row["latitude"], "longitude": row["longitude"]},
                  "observation_time": row["observation_time"], "valid_time": row["valid_time"],
                  "temporal_mode": "observation", "source": "complete-p5-data", "quality": "mixed",
                  "data": {"zone_id": row["zone_id"], "latitude": row["latitude"], "longitude": row["longitude"]},
                  "metadata": {"dataset": "p5_data.json", "upstream_equivalent": "ECMWF/Copernicus observation export",
                               "source_file": str(self.path),
                               "synthetic_fields": row.get("synthetic_field_count", 0),
                               "real_fields": row.get("real_field_count", 0)}}
        data = common["data"]
        if record_type == "sst":
            data.update(sst_celsius=values[field], gradient_celsius_per_km=None, thermal_front_delta_celsius=None)
        elif record_type == "chlorophyll":
            data["chlorophyll_a_mg_m3"] = values[field]
        elif record_type == "wind":
            direction = math.degrees(math.atan2(values.get("wind_u", 0.0), values.get("wind_v", 0.0))) % 360
            data.update(wind_speed_knots=values[field], wind_speed_ms=values.get("wind_speed") or values[field] * 0.514444,
                        wind_direction_deg=direction, wind_direction="UNKNOWN", gust_knots=None)
        elif record_type == "wave":
            data.update(significant_wave_height_m=values[field], wave_period_s=values.get("peak_wave_period"),
                        wave_direction_deg=values.get("mean_wave_direction"))
        elif record_type == "swell":
            data.update(swell_height_m=values[field], swell_period_s=values.get("swell_period_s"),
                        swell_direction_deg=values.get("swell_direction_deg"))
        elif record_type == "tide":
            data.update(water_level_m=values[field], tide_phase="unknown", next_high_tide=None, next_low_tide=None)
        elif record_type == "currents":
            data.update(current_speed_knots=values[field], current_direction_deg=values.get("current_direction_deg"))
        return common

    def query(self, record_type: str, query: Optional[P5Query] = None) -> P5Response:
        if record_type not in RECORD_TYPES:
            raise P5Error(f"unknown record_type {record_type!r}; expected one of {', '.join(RECORD_TYPES)}")
        q = query or P5Query()
        if record_type not in self.FIELD_TYPES:
            return P5Response("unavailable", record_type, [],
                [{"zone_id": row["zone_id"], "reason": "field_not_present_in_complete_dataset"} for row in self._rows],
                metadata={"source": self.name, "synthetic": False, "dataset_file": str(self.path)})
        selected = self._select_rows(q)
        records = [record for row in selected if (record := self._record(row, record_type))]
        return P5Response("success" if records else "unavailable", record_type, records,
            [] if records else [{"zone_id": "complete", "reason": "no_matching_observation"}],
            query={**q.to_params(), "resolved_at": records[0]["valid_time"] if records else None},
            metadata={"source": self.name, "contract_version": "p5-complete-v1", "synthetic": False,
                      "dataset_file": str(self.path), "selection": []})


# --------------------------------------------------------------- registry
_SOURCE: Optional[P5DataSource] = None


def get_p5_source() -> P5DataSource:
    """The active P5 source: HTTP, complete enriched data, or mock data."""
    global _SOURCE
    if _SOURCE is None:
        url = os.environ.get("P5_API_URL")
        source_kind = os.environ.get("P5_SOURCE", "mock").lower()
        if url:
            from backend.p5.client import HttpP5DataSource
            _SOURCE = HttpP5DataSource(url)
        elif source_kind == "complete":
            _SOURCE = CompleteP5DataSource(os.environ.get("P5_COMPLETE_DATA_PATH"))
        else:
            _SOURCE = MockP5DataSource(os.environ.get("P5_DATA_DIR"))
    return _SOURCE


def set_p5_source(source: Optional[P5DataSource]) -> None:
    """Inject a P5 backend (tests, live ingestion). None resets to the default."""
    global _SOURCE
    _SOURCE = source
