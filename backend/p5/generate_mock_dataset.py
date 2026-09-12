"""P5 mock marine dataset generator.

Produces a deterministic synthetic dataset in the frozen P5 -> P4 normalized
contract, for every data type P5 owns: PFZ candidates, SST, chlorophyll-a,
wind, significant wave, swell, tide, currents, restrictions and historical
series. It contains raw/normalized observations only — no opportunity score,
risk score, ranking or recommendation (those belong to P6/P3).

Golden records: ZONE_A/B/C are taken verbatim from the Mangalore fixture
(backend/agents/mocks/fixtures/mangalore_scenario.py) at the reference time,
so the P3/P4/P6 golden scenario holds on this dataset too. Nine further zones
off the Karnataka coast add variety (one blocked, one conditional, one rough).

Usage (from the repo root):
    python -m backend.p5.generate_mock_dataset          # write data/mock/p5/
    python -m backend.p5.generate_mock_dataset --check  # verify files on disk match a fresh run
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:  # allow `python backend/p5/generate_mock_dataset.py`
    sys.path.insert(0, str(REPO_ROOT))

from backend.agents.mocks.fixtures.mangalore_scenario import MANGALORE_REFERENCE, MANGALORE_ZONES  # noqa: E402

GENERATOR_VERSION = "1.0.0"
CONTRACT_VERSION = "p5-normalized-v1"
SEED = 20260911
# Fixed, not "now": the dataset must be byte-identical on every run.
REFERENCE_TIME = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
MODEL_RUN_TIME = REFERENCE_TIME - timedelta(hours=6)
FORECAST_HOURS = list(range(0, 48, 6))  # 8 steps, 6-hourly out to +42 h — covers "tomorrow morning"
SATELLITE_DAYS = 7
PFZ_ADVISORY_DAYS = [0, 2, 4]  # INCOIS issues advisories ~3x a week
HISTORY_DAYS = 90
FRONT_WIDTH_KM = 5.0  # gradient = front delta / front width (0.9 °C -> 0.18 °C/km, as in the contract)
KNOT_MS = 0.514444
OUT_DIR = REPO_ROOT / "data" / "mock" / "p5"
SOURCE = "synthetic"

TEMPORAL_MODE = {
    "pfz": "latest_available", "sst": "latest_available", "chlorophyll": "latest_available",
    "restrictions": "latest_available",
    "wind": "forecast", "wave": "forecast", "swell": "forecast", "tide": "forecast", "currents": "forecast",
    "historical": "historical",
}

LATLON_UNITS = {"latitude": "degrees_north", "longitude": "degrees_east"}
UNITS: Dict[str, Dict[str, str]] = {
    "pfz": {**LATLON_UNITS, "distance_nm": "nmi", "bearing_deg": "degrees_true (from harbor to zone)",
            "pfz_confidence": "fraction 0-1", "depth_m": "m (water depth)"},
    "sst": {**LATLON_UNITS, "sst_celsius": "degC", "gradient_celsius_per_km": "degC/km", "thermal_front_delta_celsius": "degC"},
    "chlorophyll": {**LATLON_UNITS, "chlorophyll_a_mg_m3": "mg/m3"},
    "wind": {"wind_speed_knots": "kn", "wind_speed_ms": "m/s", "wind_direction_deg": "degrees_true (direction wind blows FROM)", "gust_knots": "kn"},
    "wave": {"significant_wave_height_m": "m", "wave_period_s": "s", "wave_direction_deg": "degrees_true (direction waves come FROM)"},
    "swell": {"swell_height_m": "m", "swell_period_s": "s", "swell_direction_deg": "degrees_true (direction swell comes FROM)"},
    "tide": {"water_level_m": "m above chart datum"},
    "currents": {"current_speed_knots": "kn", "current_direction_deg": "degrees_true (direction current flows TOWARDS)"},
    "restrictions": {},
    "historical": {},
}
# Measured fields: None here means "missing" and must be declared in metadata.missing_fields.
MEASURED = {t: [k for k in u if k not in LATLON_UNITS] for t, u in UNITS.items()}

UPSTREAM = {
    "pfz": ("SYNTHETIC_INCOIS_PFZ", "INCOIS PFZ advisory (GeoServer WFS PFZ_Automation:pfzlines)"),
    "sst": ("SYNTHETIC_MUR_SST_L4", "NOAA CoastWatch ERDDAP jplMURSST41 (MUR SST L4, ~1 km, daily)"),
    "chlorophyll": ("SYNTHETIC_VIIRS_CHLA_L3", "NOAA CoastWatch ERDDAP noaacwNPPVIIRSSQchlaDaily (VIIRS Chl-a, daily)"),
    "wind": ("SYNTHETIC_ECMWF_IFS_WIND", "Open-Meteo Forecast wind_speed_10m / wind_direction_10m / wind_gusts_10m"),
    "wave": ("SYNTHETIC_ECMWF_WAM", "Open-Meteo Marine wave_height / wave_period / wave_direction"),
    "swell": ("SYNTHETIC_ECMWF_WAM_SWELL", "Open-Meteo Marine swell_wave_height / swell_wave_period / swell_wave_direction"),
    "tide": ("SYNTHETIC_HARMONIC_TIDE", "INCOIS / Survey of India tide predictions (harmonic constituents)"),
    "currents": ("SYNTHETIC_OCEAN_CURRENTS", "Open-Meteo Marine ocean_current_velocity / ocean_current_direction"),
    "restrictions": ("SYNTHETIC_GAZETTE_RESTRICTIONS", "State Fisheries Dept / Coast Guard / NAVAREA VIII notices"),
    "historical": ("SYNTHETIC_DAILY_ARCHIVE", "NOAA ERDDAP archives / Open-Meteo historical (ERA5)"),
}

# P6/P3 outputs that must never appear in P5 data.
FORBIDDEN_KEYS = {
    "opportunity_score", "risk_score", "rank", "ranked_zones", "severity", "grade", "recommendation",
    "eligible", "decision_status", "is_safe", "trend", "productivity_index",
}

CARDINALS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
SPECIES_POOL = [
    "Indian Mackerel", "Oil Sardine", "Seer Fish", "Silver Pomfret", "Ribbon Fish",
    "Squid", "Yellowfin Tuna", "Anchovy", "Barracuda", "Kingfish",
]


# ------------------------------------------------------------------ helpers
def iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def rng_for(*keys: Any) -> random.Random:
    """Independent deterministic stream per (zone, data type, ...), so adding a
    zone or a type never shifts the numbers of the others."""
    return random.Random(":".join([str(SEED), *map(str, keys)]))


def cardinal(deg: float) -> str:
    return CARDINALS[round((deg % 360) / 22.5) % 16]


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = math.radians
    a = math.sin(r(lat2 - lat1) / 2) ** 2 + math.cos(r(lat1)) * math.cos(r(lat2)) * math.sin(r(lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a)) / 1.852


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = math.radians
    y = math.sin(r(lon2 - lon1)) * math.cos(r(lat2))
    x = math.cos(r(lat1)) * math.sin(r(lat2)) - math.sin(r(lat1)) * math.cos(r(lat2)) * math.cos(r(lon2 - lon1))
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def coast_lon(lat: float) -> float:
    """Rough Karnataka coastline (Kasaragod–Udupi) as longitude per latitude."""
    return 74.84 - 0.33 * (lat - 12.87)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def diurnal(base: float, hour: float, amp: float, phase_h: float, noise: float, rng: random.Random) -> float:
    """Smooth daily swing anchored so hour 0 returns `base` exactly."""
    swing = amp * (math.sin(2 * math.pi * (hour + phase_h) / 24) - math.sin(2 * math.pi * phase_h / 24))
    return base * (1 + swing) + (0.0 if hour == 0 else rng.gauss(0, noise))


# -------------------------------------------------------------------- zones
@dataclass
class Zone:
    zone_id: str
    latitude: float
    longitude: float
    distance_nm: float
    bearing_deg: float
    depth_m: float
    species: List[str]
    golden: bool
    base: Dict[str, float]
    restriction: Dict[str, Any]
    extras: Dict[str, Any] = field(default_factory=dict)

    @property
    def location(self) -> Dict[str, Any]:
        return {"name": f"{self.zone_id} off {MANGALORE_REFERENCE['name']}", "latitude": self.latitude, "longitude": self.longitude}


def _front_delta(text: str) -> float:
    m = re.search(r"([0-9.]+)\s*°C", text)
    if not m:
        raise ValueError(f"cannot parse SST front delta from fixture text: {text!r}")
    return float(m.group(1))


def golden_zones() -> List[Zone]:
    zones = []
    for z in MANGALORE_ZONES:
        rng = rng_for(z["zone_id"], "golden")
        delta = _front_delta(z["sst_gradient_delta"])
        zones.append(Zone(
            zone_id=z["zone_id"], latitude=z["latitude"], longitude=z["longitude"],
            distance_nm=z["distance_nm"], bearing_deg=CARDINALS.index(z["bearing"]) * 22.5,
            depth_m=z["depth_m"], species=list(z["species"]), golden=True,
            base={
                "sst_celsius": z["sst_celsius"],
                "thermal_front_delta_celsius": delta,
                "gradient_celsius_per_km": round(delta / FRONT_WIDTH_KM, 3),
                "chlorophyll_a_mg_m3": z["chlorophyll_a_mg_m3"],
                "pfz_confidence": z["pfz_confidence"],
                "wind_speed_knots": z["wind_speed_knots"],
                "gust_knots": z["wind_gust_knots"],
                "wind_direction_deg": z["wind_direction_deg"],
                "significant_wave_height_m": z["wave_height_m"],
                "wave_period_s": z["wave_period_sec"],
                "wave_direction_deg": z["wave_direction_deg"],
                "swell_height_m": z["swell_height_m"],
                "swell_period_s": z["swell_period_sec"],
                "swell_direction_deg": z["swell_direction_deg"],
                # not in the fixture — generated
                "current_speed_knots": round(rng.uniform(0.4, 1.0), 2),
                "current_direction_deg": round(rng.uniform(160, 195)),
            },
            restriction={
                "restricted": z["restricted"],
                "regulatory_status": z["regulatory_status"],
                "restriction_reason": z["restriction_reason"],
                "valid_from": "2026-01-01T00:00:00Z" if z["restricted"] else None,
                "valid_until": None,
            },
        ))
    return zones


# (zone_id, lat, lon, overrides)
EXTRA_ZONE_SPECS: List[tuple] = [
    ("ZONE_D", 13.05, 74.55, {}),
    ("ZONE_E", 13.20, 74.45, {"sst_anomaly": True}),  # carries a warm-water event in its SST history
    ("ZONE_F", 12.70, 74.60, {}),
    ("ZONE_G", 12.60, 74.75, {}),
    ("ZONE_H", 13.35, 74.35, {"wind_speed_knots": 27.0, "significant_wave_height_m": 3.3}),  # rough-sea case
    ("ZONE_I", 12.85, 74.40, {"restriction": {
        "restricted": False, "regulatory_status": "CONDITIONAL",
        "restriction_reason": "Mechanised trawling prohibited; traditional and gillnet craft permitted",
        "valid_from": "2026-08-01T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z"}}),
    ("ZONE_J", 12.95, 74.62, {}),
    ("ZONE_K", 13.10, 74.25, {"restriction": {
        "restricted": True, "regulatory_status": "BLOCKED",
        "restriction_reason": "Naval firing practice area (NAVAREA VIII warning)",
        "valid_from": "2026-09-10T00:00:00Z", "valid_until": "2026-09-14T23:59:59Z"}}),
    ("ZONE_L", 12.55, 74.45, {}),
]


def extra_zones() -> List[Zone]:
    h = MANGALORE_REFERENCE
    zones = []
    for zid, lat, lon, over in EXTRA_ZONE_SPECS:
        rng = rng_for(zid, "base")
        off_km = (coast_lon(lat) - lon) * 111.32 * math.cos(math.radians(lat))
        wind = over.get("wind_speed_knots", round(rng.uniform(8, 23), 1))
        wind_dir = round(rng.uniform(225, 265))
        wave = over.get("significant_wave_height_m", round(clamp(0.35 + 0.085 * wind + rng.gauss(0, 0.2), 0.5, 3.0), 2))
        delta = round(rng.uniform(0.2, 1.2), 2)
        zones.append(Zone(
            zone_id=zid, latitude=lat, longitude=lon,
            distance_nm=round(haversine_nm(h["latitude"], h["longitude"], lat, lon), 1),
            bearing_deg=round(bearing_deg(h["latitude"], h["longitude"], lat, lon), 1),
            depth_m=round(18 + off_km * 1.4 + rng.uniform(-4, 6)),
            species=sorted(rng.sample(SPECIES_POOL, 2)), golden=False,
            base={
                "sst_celsius": round(rng.uniform(27.9, 29.3), 2),
                "thermal_front_delta_celsius": delta,
                "gradient_celsius_per_km": round(delta / FRONT_WIDTH_KM, 3),
                "chlorophyll_a_mg_m3": round(0.35 + 3.2 * math.exp(-off_km / 35) * rng.uniform(0.75, 1.3), 2),
                "pfz_confidence": round(rng.uniform(0.45, 0.9), 2),
                "wind_speed_knots": wind,
                "gust_knots": round(wind * rng.uniform(1.2, 1.4), 1),
                "wind_direction_deg": wind_dir,
                "significant_wave_height_m": wave,
                "wave_period_s": round(clamp(5.5 + 0.12 * wind + rng.gauss(0, 0.4), 5.0, 10.0), 1),
                "wave_direction_deg": wind_dir - round(rng.uniform(3, 10)),
                "swell_height_m": round(rng.uniform(0.5, 1.9), 2),
                "swell_period_s": round(rng.uniform(7, 12), 1),
                "swell_direction_deg": round(rng.uniform(215, 245)),
                "current_speed_knots": round(rng.uniform(0.2, 1.2), 2),
                "current_direction_deg": round(rng.uniform(150, 200)),
            },
            restriction=over.get("restriction", {
                "restricted": False, "regulatory_status": "CLEAR", "restriction_reason": None,
                "valid_from": None, "valid_until": None,
            }),
            extras={"sst_anomaly": over.get("sst_anomaly", False)},
        ))
    return zones


# ----------------------------------------------------------------- records
def envelope(rtype: str, zone: Zone, data: Dict[str, Any], *, observation_time: Optional[datetime] = None,
             valid_time: Optional[datetime] = None, quality: str = "high", missing_fields: Optional[List[str]] = None,
             missing_reason: Optional[str] = None, golden: bool = False, **meta: Any) -> Dict[str, Any]:
    dataset, upstream = UPSTREAM[rtype]
    stamp = iso(valid_time or observation_time)
    metadata: Dict[str, Any] = {
        "synthetic": True,
        "dataset": dataset,
        "upstream_equivalent": upstream,
        "units": UNITS[rtype],
        "missing_fields": missing_fields or [],
        "missing_reason": missing_reason,
        "golden_fixture": golden,
        "generator": f"backend.p5.generate_mock_dataset {GENERATOR_VERSION}",
        "seed": SEED,
        **meta,
    }
    return {
        "record_id": f"{rtype}:{zone.zone_id}:{stamp}",
        "record_type": rtype,
        "contract_version": CONTRACT_VERSION,
        "zone_id": zone.zone_id,
        "location": zone.location,
        "observation_time": iso(observation_time),
        "valid_time": iso(valid_time),
        "temporal_mode": TEMPORAL_MODE[rtype],
        "source": SOURCE,
        "quality": quality,
        "data": data,
        "metadata": metadata,
    }


def satellite_records(zone: Zone) -> List[Dict[str, Any]]:
    """SST and chlorophyll: one observation per day, latest first. Satellite = latest_available."""
    out = []
    b = zone.base
    srng, crng = rng_for(zone.zone_id, "sst"), rng_for(zone.zone_id, "chl")
    sst_drift = srng.uniform(-0.05, 0.05)
    for d in range(SATELLITE_DAYS):
        obs = (REFERENCE_TIME - timedelta(days=d + 1)).replace(hour=9)
        latest_golden = zone.golden and d == 0

        # ---- SST (L4 analysis: gap-free, but front detection can fail)
        sst = b["sst_celsius"] if d == 0 else round(b["sst_celsius"] + sst_drift * d + srng.gauss(0, 0.12), 2)
        delta: Optional[float] = b["thermal_front_delta_celsius"] if d == 0 else round(clamp(b["thermal_front_delta_celsius"] * (1 + srng.gauss(0, 0.15)), 0.05, 2.0), 2)
        front_failed = not latest_golden and d > 0 and srng.random() < 0.06
        if front_failed:
            delta = None
        grad = None if delta is None else (b["gradient_celsius_per_km"] if d == 0 else round(delta / FRONT_WIDTH_KM, 3))
        missing = ["gradient_celsius_per_km", "thermal_front_delta_celsius"] if front_failed else []
        out.append(envelope(
            "sst", zone,
            {"zone_id": zone.zone_id, "latitude": zone.latitude, "longitude": zone.longitude,
             "sst_celsius": sst, "gradient_celsius_per_km": grad, "thermal_front_delta_celsius": delta,
             "observation_time": iso(obs), "temporal_mode": "latest_available"},
            observation_time=obs, quality="degraded" if front_failed else "high",
            missing_fields=missing, missing_reason="front_detection_failed" if front_failed else None,
            golden=latest_golden, spatial_resolution_km=1.0, days_before_reference=d + 1,
        ))

        # ---- Chlorophyll (L3: cloud gaps are common during the monsoon)
        chl: Optional[float] = b["chlorophyll_a_mg_m3"] if d == 0 else round(b["chlorophyll_a_mg_m3"] * math.exp(crng.gauss(0, 0.2)), 3)
        cloudy = not latest_golden and d > 0 and crng.random() < 0.15
        if cloudy:
            chl = None
        out.append(envelope(
            "chlorophyll", zone,
            {"zone_id": zone.zone_id, "latitude": zone.latitude, "longitude": zone.longitude,
             "chlorophyll_a_mg_m3": chl, "observation_time": iso(obs), "temporal_mode": "latest_available"},
            observation_time=obs, quality="missing" if cloudy else "high",
            missing_fields=["chlorophyll_a_mg_m3"] if cloudy else [], missing_reason="cloud_cover" if cloudy else None,
            golden=latest_golden, spatial_resolution_km=0.75, days_before_reference=d + 1,
            note="Chlorophyll-a is a primary-productivity proxy, not a measure of fish presence",
        ))
    return out


def pfz_records(zone: Zone) -> List[Dict[str, Any]]:
    """PFZ candidates (not recommendations) from the last three advisories."""
    out = []
    rng = rng_for(zone.zone_id, "pfz")
    for d in PFZ_ADVISORY_DAYS:
        if not zone.golden and d > 0 and rng.random() < 0.25:
            continue  # zone not in that advisory — absence, not a zero-confidence record
        issued = (REFERENCE_TIME - timedelta(days=d + 1)).replace(hour=11, minute=30)
        conf = zone.base["pfz_confidence"] if d == 0 else round(clamp(zone.base["pfz_confidence"] + rng.gauss(0, 0.06), 0.3, 0.97), 2)
        out.append(envelope(
            "pfz", zone,
            {"zone_id": zone.zone_id, "latitude": zone.latitude, "longitude": zone.longitude,
             "distance_nm": zone.distance_nm, "bearing_deg": zone.bearing_deg, "pfz_confidence": conf,
             "species": zone.species, "depth_m": zone.depth_m,
             "observation_time": iso(issued), "temporal_mode": "latest_available"},
            observation_time=issued, golden=zone.golden and d == 0, advisory_age_days=d + 1,
        ))
    return out


# harmonic tide: (constituent, amplitude m, period h, phase rad)
TIDE_CONSTITUENTS = [("M2", 0.55, 12.4206, 0.9), ("S2", 0.21, 12.0, 1.6), ("K1", 0.34, 23.9345, 2.3), ("O1", 0.17, 25.8193, 0.4)]
TIDE_MSL_M = 1.05


def tide_level(t_h: float, lag_h: float) -> float:
    return TIDE_MSL_M + sum(a * math.cos(2 * math.pi * (t_h - lag_h) / p - ph) for _, a, p, ph in TIDE_CONSTITUENTS)


def next_extreme(t_h: float, lag_h: float, high: bool) -> float:
    step = 0.1  # 6 minutes
    prev = tide_level(t_h + step, lag_h) - tide_level(t_h, lag_h)
    t = t_h + step
    while t < t_h + 27:
        cur = tide_level(t + step, lag_h) - tide_level(t, lag_h)
        if (high and prev > 0 >= cur) or (not high and prev < 0 <= cur):
            return t
        prev, t = cur, t + step
    raise RuntimeError("no tidal extreme found within 27 h")


def forecast_records(zone: Zone) -> List[Dict[str, Any]]:
    """Wind, wave, swell, tide and currents: 3-hourly forecast steps. Forecast = valid_time only."""
    out = []
    b = zone.base
    wr, vr, sr, cr = (rng_for(zone.zone_id, k) for k in ("wind", "wave", "swell", "currents"))
    gust_ratio = b["gust_knots"] / b["wind_speed_knots"]
    tide_lag = (zone.longitude - 74.0) * 0.4
    common = {"model_run_time": iso(MODEL_RUN_TIME)}
    for h in FORECAST_HOURS:
        vt = REFERENCE_TIME + timedelta(hours=h)
        lead = h + 6
        q = "high" if lead <= 24 else "moderate"
        step0_golden = zone.golden and h == 0
        meta = {**common, "lead_time_hours": lead}

        # ---- wind
        spd = round(max(1.0, diurnal(b["wind_speed_knots"], h, 0.18, 9, 0.8, wr)), 1)
        gust: Optional[float] = b["gust_knots"] if h == 0 else round(spd * gust_ratio, 1)
        wdir = round(b["wind_direction_deg"] + (0 if h == 0 else 8 * math.sin(2 * math.pi * h / 24) + wr.gauss(0, 3))) % 360
        no_gust = not step0_golden and h > 0 and wr.random() < 0.05
        if no_gust:
            gust = None
        out.append(envelope(
            "wind", zone,
            {"zone_id": zone.zone_id, "wind_speed_knots": spd, "wind_speed_ms": round(spd * KNOT_MS, 2),
             "wind_direction_deg": wdir, "wind_direction": cardinal(wdir), "gust_knots": gust,
             "observation_time": None, "valid_time": iso(vt), "temporal_mode": "forecast"},
            valid_time=vt, quality="degraded" if no_gust else q,
            missing_fields=["gust_knots"] if no_gust else [], missing_reason="not_provided_by_model" if no_gust else None,
            golden=step0_golden, resolution_km=9.0, **meta,
        ))

        # ---- significant wave
        hs = round(max(0.2, diurnal(b["significant_wave_height_m"], h, 0.08, 12, 0.05, vr)), 2)
        per: Optional[float] = b["wave_period_s"] if h == 0 else round(b["wave_period_s"] + vr.gauss(0, 0.25), 1)
        no_period = not step0_golden and h > 0 and vr.random() < 0.04
        if no_period:
            per = None
        vdir = round(b["wave_direction_deg"] + (0 if h == 0 else vr.gauss(0, 4))) % 360
        out.append(envelope(
            "wave", zone,
            {"zone_id": zone.zone_id, "significant_wave_height_m": hs, "wave_period_s": per,
             "wave_direction_deg": vdir, "valid_time": iso(vt), "temporal_mode": "forecast"},
            valid_time=vt, quality="degraded" if no_period else q,
            missing_fields=["wave_period_s"] if no_period else [], missing_reason="not_provided_by_model" if no_period else None,
            golden=step0_golden, resolution_km=9.0, **meta,
        ))

        # ---- swell (long-period, changes slowly)
        sh = b["swell_height_m"] if h == 0 else round(max(0.1, b["swell_height_m"] * (1 + 0.03 * h / 3) + sr.gauss(0, 0.04)), 2)
        sp = b["swell_period_s"] if h == 0 else round(b["swell_period_s"] + sr.gauss(0, 0.2), 1)
        sdir = round(b["swell_direction_deg"] + (0 if h == 0 else sr.gauss(0, 2))) % 360
        out.append(envelope(
            "swell", zone,
            {"zone_id": zone.zone_id, "swell_height_m": sh, "swell_period_s": sp,
             "swell_direction_deg": sdir, "valid_time": iso(vt), "temporal_mode": "forecast"},
            valid_time=vt, quality=q, golden=step0_golden, resolution_km=9.0, **meta,
        ))

        # ---- tide (harmonic prediction)
        t_h = h + 0.0
        lvl = tide_level(t_h, tide_lag)
        slope = (tide_level(t_h + 0.1, tide_lag) - tide_level(t_h - 0.1, tide_lag)) / 0.2
        if abs(slope) < 0.03:
            phase = "high_slack" if lvl > TIDE_MSL_M else "low_slack"
        else:
            phase = "flood" if slope > 0 else "ebb"
        hi = REFERENCE_TIME + timedelta(hours=next_extreme(t_h, tide_lag, True))
        lo = REFERENCE_TIME + timedelta(hours=next_extreme(t_h, tide_lag, False))
        out.append(envelope(
            "tide", zone,
            {"zone_id": zone.zone_id, "water_level_m": round(lvl, 2), "tide_phase": phase,
             "next_high_tide": iso(hi.replace(second=0, microsecond=0)), "next_low_tide": iso(lo.replace(second=0, microsecond=0)),
             "valid_time": iso(vt), "temporal_mode": "forecast"},
            valid_time=vt, quality="high", constituents=[c[0] for c in TIDE_CONSTITUENTS], datum="chart_datum", **meta,
        ))

        # ---- surface currents (tidally modulated)
        cs = round(max(0.05, b["current_speed_knots"] * (1 + 0.25 * (math.sin(2 * math.pi * (h + 2) / 12.42) - math.sin(2 * math.pi * 2 / 12.42))) + (0 if h == 0 else cr.gauss(0, 0.04))), 2)
        cd = round(b["current_direction_deg"] + (0 if h == 0 else 15 * math.sin(2 * math.pi * h / 12.42) + cr.gauss(0, 4))) % 360
        out.append(envelope(
            "currents", zone,
            {"zone_id": zone.zone_id, "current_speed_knots": cs, "current_direction_deg": cd,
             "valid_time": iso(vt), "temporal_mode": "forecast"},
            valid_time=vt, quality=q, resolution_km=8.0, **meta,
        ))
    return out


def restriction_record(zone: Zone) -> Dict[str, Any]:
    r = zone.restriction
    notice = datetime.fromisoformat(r["valid_from"].replace("Z", "+00:00")) if r["valid_from"] else REFERENCE_TIME - timedelta(days=1)
    return envelope(
        "restrictions", zone,
        {"zone_id": zone.zone_id, "restricted": r["restricted"], "regulatory_status": r["regulatory_status"],
         "restriction_reason": r["restriction_reason"], "source": UPSTREAM["restrictions"][1],
         "valid_from": r["valid_from"], "valid_until": r["valid_until"]},
        observation_time=notice, golden=zone.golden,
        jurisdiction="Karnataka State Fisheries Dept / Indian Coast Guard",
    )


HIST_VARS = {  # variable -> (base field, unit, decimals, aggregation)
    "SST": ("sst_celsius", "degC", 2, "daily_L4_analysis"),
    "CHLOROPHYLL_A": ("chlorophyll_a_mg_m3", "mg/m3", 3, "daily_L3"),
    "WIND_SPEED": ("wind_speed_knots", "kn", 1, "daily_mean"),
    "SIGNIFICANT_WAVE_HEIGHT": ("significant_wave_height_m", "m", 2, "daily_mean"),
}


def historical_records(zone: Zone) -> List[Dict[str, Any]]:
    """Daily series for the 90 days before the reference time. Raw series only —
    no trend, change or anomaly flags (P6 computes those)."""
    out = []
    n = HISTORY_DAYS
    for var, (key, unit, dec, agg) in HIST_VARS.items():
        rng = rng_for(zone.zone_id, "hist", var)
        base = zone.base[key]
        series, e = [], 0.0
        for i in range(n):
            ts = REFERENCE_TIME - timedelta(days=n - i)
            x = i / (n - 1)  # 0 = oldest, 1 = yesterday
            e = 0.7 * e + rng.gauss(0, 1)
            if var == "SST":  # monsoon cooling dip, recovering in September
                v: Optional[float] = base - 0.8 * math.sin(math.pi * x) + 0.25 * (x - 1) + 0.12 * e
                if zone.extras.get("sst_anomaly") and 52 <= i <= 56:
                    v += 1.1
            elif var == "CHLOROPHYLL_A":  # upwelling-season bloom fading out
                v = base * (1 + 0.9 * (1 - x)) * math.exp(0.18 * e)
                if rng.random() < 0.14:
                    v = None  # cloud gap
            elif var == "WIND_SPEED":  # monsoon winds weakening
                v = max(1.0, base * (1 + 0.45 * (1 - x)) + 1.5 * e)
            else:
                v = max(0.2, base * (1 + 0.55 * (1 - x)) + 0.15 * e)
            series.append({"timestamp": iso(ts), "value": None if v is None else round(v, dec)})
        missing = sum(1 for p in series if p["value"] is None)
        last = REFERENCE_TIME - timedelta(days=1)
        out.append(envelope(
            "historical", zone,
            {"variable": var, "zone_id": zone.zone_id, "series": series, "unit": unit, "source": SOURCE},
            observation_time=last, quality="degraded" if missing else "high",
            missing_reason="cloud_cover" if missing else None,
            aggregation=agg, interval="P1D", start=series[0]["timestamp"], end=series[-1]["timestamp"],
            points=n, missing_points=missing,
        ) | {"record_id": f"historical:{zone.zone_id}:{var}"})
    return out


# -------------------------------------------------------------- validation
def validate(rec: Dict[str, Any]) -> List[str]:
    """Contract rules every record must satisfy. Returns human-readable errors."""
    errs: List[str] = []
    rid = rec.get("record_id", "?")
    for k in ("record_id", "record_type", "zone_id", "location", "observation_time", "valid_time",
              "temporal_mode", "source", "quality", "data", "metadata"):
        if k not in rec:
            errs.append(f"{rid}: missing envelope key {k}")
    if errs:
        return errs
    t, data, meta = rec["record_type"], rec["data"], rec["metadata"]
    if rec["temporal_mode"] != TEMPORAL_MODE.get(t):
        errs.append(f"{rid}: temporal_mode {rec['temporal_mode']} not allowed for {t}")
    if rec["temporal_mode"] == "forecast" and (rec["valid_time"] is None or rec["observation_time"] is not None):
        errs.append(f"{rid}: forecast must have valid_time and no observation_time")
    if rec["temporal_mode"] in ("latest_available", "historical") and (rec["observation_time"] is None or rec["valid_time"] is not None):
        errs.append(f"{rid}: observation must have observation_time and no valid_time")
    if data.get("zone_id") != rec["zone_id"]:
        errs.append(f"{rid}: data.zone_id does not match envelope")
    lat, lon = rec["location"]["latitude"], rec["location"]["longitude"]
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        errs.append(f"{rid}: location out of range")
    for k, v in data.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and k not in UNITS[t]:
            errs.append(f"{rid}: numeric field {k} has no unit in metadata.units")
    declared = set(meta["missing_fields"])
    actual = {k for k in MEASURED[t] if k in data and data[k] is None}
    if declared != actual:
        errs.append(f"{rid}: missing_fields {sorted(declared)} != null measured fields {sorted(actual)}")
    if actual and rec["quality"] not in ("degraded", "missing"):
        errs.append(f"{rid}: null measurements but quality={rec['quality']}")
    if t == "historical":
        nulls = sum(1 for p in data["series"] if p["value"] is None)
        if nulls != meta["missing_points"]:
            errs.append(f"{rid}: missing_points {meta['missing_points']} != {nulls} null series values")
    blob = json.dumps(data)
    for bad in FORBIDDEN_KEYS:
        if f'"{bad}"' in blob:
            errs.append(f"{rid}: P6/P3 field {bad!r} must not appear in P5 data")
    return errs


def check_golden(records: List[Dict[str, Any]]) -> List[str]:
    """The fixture zones must reproduce the fixture exactly at the reference time."""
    errs = []
    idx = {(r["record_type"], r["zone_id"]): r for r in records if r["metadata"].get("golden_fixture")}
    for z in MANGALORE_ZONES:
        zid = z["zone_id"]
        expect = {
            "sst": {"sst_celsius": z["sst_celsius"], "thermal_front_delta_celsius": _front_delta(z["sst_gradient_delta"])},
            "chlorophyll": {"chlorophyll_a_mg_m3": z["chlorophyll_a_mg_m3"]},
            "pfz": {"pfz_confidence": z["pfz_confidence"], "distance_nm": z["distance_nm"], "species": z["species"]},
            "wind": {"wind_speed_knots": z["wind_speed_knots"], "gust_knots": z["wind_gust_knots"], "wind_direction_deg": z["wind_direction_deg"]},
            "wave": {"significant_wave_height_m": z["wave_height_m"], "wave_period_s": z["wave_period_sec"], "wave_direction_deg": z["wave_direction_deg"]},
            "swell": {"swell_height_m": z["swell_height_m"], "swell_period_s": z["swell_period_sec"], "swell_direction_deg": z["swell_direction_deg"]},
            "restrictions": {"restricted": z["restricted"], "regulatory_status": z["regulatory_status"], "restriction_reason": z["restriction_reason"]},
        }
        for rtype, fields in expect.items():
            rec = idx.get((rtype, zid))
            if rec is None:
                errs.append(f"golden {rtype}:{zid} record missing")
                continue
            for k, v in fields.items():
                if rec["data"].get(k) != v:
                    errs.append(f"golden {rtype}:{zid}.{k} = {rec['data'].get(k)!r}, fixture = {v!r}")
    return errs


# ------------------------------------------------------------------ output
def build() -> Dict[str, Any]:
    zones = golden_zones() + extra_zones()
    by_type: Dict[str, List[Dict[str, Any]]] = {t: [] for t in TEMPORAL_MODE}
    for z in zones:
        for rec in pfz_records(z) + satellite_records(z) + forecast_records(z) + [restriction_record(z)] + historical_records(z):
            by_type[rec["record_type"]].append(rec)
    return {"zones": zones, "by_type": by_type}


def _jsonl(records: List[Dict[str, Any]]) -> bytes:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records).encode("utf-8")


def _flat_csv(by_type: Dict[str, List[Dict[str, Any]]]) -> bytes:
    """One row per non-historical record, for spreadsheets and pandas."""
    fixed = ["record_id", "record_type", "zone_id", "location_name", "latitude", "longitude",
             "observation_time", "valid_time", "temporal_mode", "source", "quality", "missing_fields"]
    rows, data_cols = [], set()
    for t, recs in by_type.items():
        if t == "historical":
            continue
        for r in recs:
            row = {"record_id": r["record_id"], "record_type": t, "zone_id": r["zone_id"],
                   "location_name": r["location"]["name"], "latitude": r["location"]["latitude"],
                   "longitude": r["location"]["longitude"], "observation_time": r["observation_time"],
                   "valid_time": r["valid_time"], "temporal_mode": r["temporal_mode"], "source": r["source"],
                   "quality": r["quality"], "missing_fields": ";".join(r["metadata"]["missing_fields"])}
            for k, v in r["data"].items():
                if k in row or k in ("latitude", "longitude"):
                    continue
                data_cols.add(k)
                row[k] = ";".join(v) if isinstance(v, list) else v
            rows.append(row)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fixed + sorted(data_cols), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _history_csv(records: List[Dict[str, Any]]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["zone_id", "variable", "timestamp", "value", "unit"])
    for r in records:
        for p in r["data"]["series"]:
            w.writerow([r["zone_id"], r["data"]["variable"], p["timestamp"], "" if p["value"] is None else p["value"], r["data"]["unit"]])
    return buf.getvalue().encode("utf-8")


def render(built: Dict[str, Any]) -> Dict[str, bytes]:
    by_type = built["by_type"]
    files = {f"{t}.jsonl": _jsonl(recs) for t, recs in by_type.items()}
    files["p5_mock_records.csv"] = _flat_csv(by_type)
    files["historical_points.csv"] = _history_csv(by_type["historical"])
    counts = {t: len(recs) for t, recs in by_type.items()}
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "generator": "backend/p5/generate_mock_dataset.py",
        "generator_version": GENERATOR_VERSION,
        "seed": SEED,
        "reference_time": iso(REFERENCE_TIME),
        "model_run_time": iso(MODEL_RUN_TIME),
        "region": {**MANGALORE_REFERENCE, "bbox": [74.2, 12.5, 75.1, 13.4]},
        "synthetic": True,
        "record_counts": counts,
        "total_records": sum(counts.values()),
        "historical_points": sum(r["metadata"]["points"] for r in by_type["historical"]),
        "zones": [{"zone_id": z.zone_id, "latitude": z.latitude, "longitude": z.longitude, "golden_fixture": z.golden,
                   "regulatory_status": z.restriction["regulatory_status"]} for z in built["zones"]],
        "temporal_semantics": {
            "latest_available": "satellite/advisory/regulatory observations: observation_time set, valid_time null",
            "forecast": "model forecasts: valid_time set, observation_time null, metadata.model_run_time + lead_time_hours",
            "historical": "daily series in data.series; observation_time = last point",
        },
        "missing_data": "measured fields that are unavailable are null, listed in metadata.missing_fields with "
                        "metadata.missing_reason, and quality is 'degraded' (some fields) or 'missing' (primary value)",
        "files": {name: {"sha256": hashlib.sha256(b).hexdigest(), "lines": b.count(b"\n")} for name, b in sorted(files.items())},
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    ap.add_argument("--check", action="store_true", help="verify existing files match a fresh generation")
    args = ap.parse_args()

    built = build()
    records = [r for recs in built["by_type"].values() for r in recs]
    errors = [e for r in records for e in validate(r)] + check_golden(records)
    if errors:
        print(f"{len(errors)} contract violations:", *errors[:30], sep="\n  ")
        return 1

    files = render(built)
    if args.check:
        stale = [n for n, b in files.items() if not (args.out / n).exists() or (args.out / n).read_bytes() != b]
        print("dataset up to date" if not stale else f"stale or missing: {', '.join(stale)}")
        return 1 if stale else 0

    args.out.mkdir(parents=True, exist_ok=True)
    for name, b in files.items():
        (args.out / name).write_bytes(b)
    counts = {t: len(v) for t, v in built["by_type"].items()}
    print(f"wrote {sum(counts.values())} records to {args.out}")
    for t, c in counts.items():
        print(f"  {t:<13}{c:>5}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
