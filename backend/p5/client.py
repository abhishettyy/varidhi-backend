"""HTTP client for the P5 data service — same interface as MockP5DataSource.

Used automatically by get_p5_source() when P5_API_URL is set, so P4 adapters
talk to a remote P5 service without any code change.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from backend.p5.source import P5Error, P5Query, P5Response


class HttpP5DataSource:
    name = "p5-http"

    def __init__(self, base_url: str = "", *, client: Optional[httpx.Client] = None, timeout: float = 10.0):
        self._client = client or httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            res = self._client.get(path, params=params)
        except httpx.HTTPError as e:  # network failure -> P4 reports status "error"
            raise ConnectionError(f"P5 service unreachable: {e}") from e
        if res.status_code in (400, 404, 422):
            raise P5Error(res.json().get("detail", res.text))
        res.raise_for_status()
        return res.json()

    def query(self, record_type: str, query: Optional[P5Query] = None) -> P5Response:
        return P5Response.from_dict(self._get(f"/p5/v1/{record_type}", (query or P5Query()).to_params()))

    def zones(self) -> List[Dict[str, Any]]:
        return self._get("/p5/v1/zones")["zones"]

    def describe(self) -> Dict[str, Any]:
        return self._get("/p5/v1/describe")
