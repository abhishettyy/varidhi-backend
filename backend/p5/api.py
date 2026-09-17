"""P5 data service over HTTP (FastAPI).

Run from the repo root:
    uvicorn backend.p5.api:app --port 8105

Endpoints (all GET, JSON):
    /p5/v1/health                 liveness + dataset summary
    /p5/v1/describe               contract version, reference time, record counts
    /p5/v1/zones                  zone catalogue
    /p5/v1/{record_type}          P5Response for pfz | sst | chlorophyll | wind | wave | swell |
                                  tide | currents | restrictions | historical
        ?lat=&lon=&radius_nm=     zones within radius of a point (default 60 nm)
        &zone_id=ZONE_A&zone_id=… explicit zones (overrides lat/lon)
        &at=2026-09-11T06:00:00Z  requested time (default: dataset reference time)
        &variable=SST&start=&end= historical series selection

Example:
    curl "http://localhost:8105/p5/v1/wind?lat=12.8681&lon=74.8427&at=2026-09-12T00:00:00Z"
"""

from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from backend.p5.source import P5DataSource, P5Error, P5Query, RECORD_TYPES, get_p5_source


def create_app(source: Optional[P5DataSource] = None) -> FastAPI:
    # The service always serves data itself — never proxies to P5_API_URL.
    src: P5DataSource = source or get_p5_source()
    app = FastAPI(title="P5 Marine Data API", version="1.0.0",
                  description="Normalized marine observations and forecasts (P5 -> P4 contract).")

    @app.get("/p5/v1/health")
    def health():
        return {"status": "ok", **src.describe()}

    @app.get("/p5/v1/describe")
    def describe():
        return src.describe()

    @app.get("/p5/v1/zones")
    def zones():
        return {"zones": src.zones()}

    @app.get("/p5/v1/{record_type}")
    def query(
        record_type: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_nm: float = 60.0,
        zone_id: Optional[List[str]] = Query(default=None),
        at: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        variable: Optional[str] = None,
    ):
        if record_type not in RECORD_TYPES:
            raise HTTPException(404, f"unknown record_type {record_type!r}; expected one of {', '.join(RECORD_TYPES)}")
        q = P5Query(latitude=lat, longitude=lon, radius_nm=radius_nm, zone_ids=zone_id,
                    at=at, start=start, end=end, variable=variable)
        try:
            return src.query(record_type, q).to_dict()
        except P5Error as e:
            raise HTTPException(400, str(e)) from e

    return app


app = create_app()
