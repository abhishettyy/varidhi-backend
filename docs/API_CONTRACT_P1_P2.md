# Varidhi Marine Intelligence Platform — Frontend API Contract (Phase 8)

> **Target Audience:** P1 (Fisherman Portal Engineers) & P2 (Researcher / GIS Portal Engineers)  
> **API Base URL (Default Local):** `http://127.0.0.1:8105`  
> **Interactive Documentation:** `http://127.0.0.1:8105/docs`

---

## 1. Architectural Principles & Integration Rules

1. **Structured Data is Authoritative**:  
   The frontend **MUST NOT** regex-parse or string-split the user-facing `message` to extract recommendations, zone IDs, scores, coordinates, or safety alerts. All UI widgets, decision badges, map markers, and recommendation cards must read directly from the structured `decision`, `zones`, `evidence`, and `visual_payload` fields.
2. **Role Controls Presentation, Not Decision Logic**:  
   Passing `role="fisherman"` vs `role="researcher"` changes the stylistic tone, technical depth, and tables of the generated `message`. The underlying P6 deterministic multi-criteria scoring, regulatory compliance check, and zone rankings remain identical and authoritative.
3. **Graceful Fallback Guarantee**:  
   If upstream LLM APIs (Gemini/OpenAI) encounter rate limits, network issues, or timeouts, the API **does not fail** with a 500. Instead, it returns `HTTP 200` with 100% deterministic rule-based results and populates `telemetry.llm_fallback = true` with a safe categorical reason (e.g. `NETWORK_UNREACHABLE`).

---

## 2. API Endpoints

### A. Health & Liveness Check
`GET /health`

Returns service status and active LLM configuration without exposing any secret keys.

#### Response (200 OK):
```json
{
  "status": "ok",
  "service": "Varidhi Marine Intelligence Platform",
  "version": "1.0.0",
  "llm_provider": "gemini",
  "llm_model": "gemini-3.7-flash"
}
```

---

### B. Natural Language Marine Query Endpoint
`POST /chat` (or alias `POST /api/chat/query`)

Executes the LangGraph agent workflow and returns multi-criteria decision analytics, candidate zone evaluations, verifiable evidence, map payloads, and persona-tailored advisories.

#### Request Schema (`ChatRequest`):
```json
{
  "query": "I'm near Mangalore. Where should I fish tomorrow morning?",
  "role": "fisherman",
  "location": {
    "name": "Mangalore",
    "latitude": 12.8681,
    "longitude": 74.8427
  },
  "session_id": "session_optional_123",
  "context_zone_id": "ZONE_B"
}
```

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | **Yes** | Natural language user query (min length 1). |
| `role` | `string` | No | Persona style: `"fisherman"`, `"researcher"`, `"maritime_operator"`, `"general"`. Defaults to `"general"`. |
| `location` | `object` | No | Optional client geographic context `{"name": "...", "latitude": ..., "longitude": ...}`. |
| `session_id` | `string` | No | Optional client tracking session ID. |
| `context_zone_id`| `string` | No | Optional active zone selected on the frontend map. |

---

#### Response Schema (`ChatResponse`):
```json
{
  "message": "### Marine Advisory for Mangalore\n\n**Safety Status:** CAUTION: Moderate Sea Conditions\n> Favorable relative to evaluated alternatives. Maintain standard maritime vigilance.\n\n#### Recommended Fishing Ground: ZONE_B (8.2 NM SSW)...",
  
  "decision": {
    "selected_zone_id": "ZONE_B",
    "status": "SELECTED",
    "opportunity_score": 66.9,
    "risk_score": 34.9,
    "regulatory_status": "ELIGIBLE",
    "ranking_score": 67.31,
    "distance_nm": 8.2,
    "bearing": "SSW",
    "species": ["Mackerel", "Sardines"],
    "latitude": 12.82,
    "longitude": 74.75,
    "reasons": [
      "Top-ranked eligible candidate with balanced opportunity and moderate sea risk."
    ],
    "safety_level": "caution_yellow",
    "action_advice": "Favorable relative to evaluated alternatives. Maintain standard maritime vigilance."
  },

  "zones": [
    {
      "zone_id": "ZONE_B",
      "status": "SELECTED",
      "opportunity_score": 66.9,
      "risk_score": 34.9,
      "regulatory_status": "ELIGIBLE",
      "ranking_score": 67.31,
      "distance_nm": 8.2,
      "bearing": "SSW",
      "species": ["Mackerel", "Sardines"],
      "latitude": 12.82,
      "longitude": 74.75,
      "reasons": []
    },
    {
      "zone_id": "ZONE_A",
      "status": "REJECTED_RISK",
      "opportunity_score": 76.6,
      "risk_score": 75.2,
      "regulatory_status": "ELIGIBLE",
      "ranking_score": null,
      "distance_nm": 14.5,
      "bearing": "WNW",
      "species": ["Kingfish"],
      "latitude": 12.95,
      "longitude": 74.65,
      "reasons": [
        "Marine risk score 75.2 exceeds project decision threshold 50.0."
      ]
    },
    {
      "zone_id": "ZONE_C",
      "status": "REJECTED_LEGAL",
      "opportunity_score": 84.5,
      "risk_score": 30.8,
      "regulatory_status": "BLOCKED",
      "ranking_score": null,
      "distance_nm": 22.0,
      "bearing": "SW",
      "species": ["Squid", "Pomfret"],
      "latitude": 12.70,
      "longitude": 74.55,
      "reasons": [
        "HARD BLOCK: Netravati Marine Ecological Sanctuary & Port Approach (MPA) - Sensitive estuarine breeding sanctuary. Fishing strictly prohibited under State Gazette."
      ]
    }
  ],

  "evidence": [
    {
      "evidence_id": "ev_a1b2c3",
      "evidence_type": "weather_observation",
      "source": "P4_TOOL_INTEGRATION",
      "summary": "Wave height 1.5m, Wind 14.2 kts",
      "metrics": {
        "wave_height_m": 1.5,
        "wind_speed_knots": 14.2
      },
      "confidence": 1.0,
      "spatial_tag": "Mangalore",
      "timestamp": "2026-09-12T02:30:00Z",
      "raw_payload": { ... }
    }
  ],

  "visual_payload": {
    "map_features_geojson": {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [74.75, 12.82] },
          "properties": {
            "zone_id": "ZONE_B",
            "status": "SELECTED",
            "recommended": true,
            "opportunity_score": 66.9,
            "risk_score": 34.9,
            "distance_nm": 8.2,
            "species": ["Mackerel", "Sardines"]
          }
        },
        {
          "type": "Feature",
          "geometry": { "type": "Point", "coordinates": [74.65, 12.95] },
          "properties": {
            "zone_id": "ZONE_A",
            "status": "REJECTED_RISK",
            "recommended": false,
            "reasons": ["Marine risk score 75.2 exceeds project decision threshold 50.0."]
          }
        }
      ]
    },
    "charts_data": [
      { "time": "00:00", "wave_height": 1.5, "wind_speed": 14.2 },
      { "time": "06:00", "wave_height": 1.65, "wind_speed": 14.91 },
      { "time": "12:00", "wave_height": 1.5, "wind_speed": 14.2 }
    ],
    "metric_badges": {
      "SST": "28.43°C",
      "Wave Height": "1.5m",
      "Wind Speed": "14.2 kts",
      "Safety": "caution_yellow",
      "Recommended Zone": "ZONE_B",
      "Ranking Score": "67.3"
    },
    "focus_zone_id": "ZONE_B",
    "highlight_layer": "zones"
  },

  "query_context": {
    "intent": "FISHING_RECOMMENDATION",
    "confidence": 0.95,
    "location": {
      "name": "Mangalore",
      "latitude": 12.8681,
      "longitude": 74.8427,
      "harbor": "Mangalore Old Port"
    },
    "time_range": {
      "raw": "tomorrow morning",
      "relative_day": "tomorrow",
      "period": "morning",
      "forecast_horizon_hours": 36
    },
    "variables": ["sea_surface_temperature", "chlorophyll"],
    "constraints": {}
  },

  "telemetry": {
    "total_pipeline_ms": 1096.13,
    "understand_query_ms": 568.10,
    "planner_ms": 0.32,
    "tool_selection_ms": 0.00,
    "executor_ms": 13.07,
    "evidence_assembly_ms": 0.21,
    "response_generation_ms": 514.24,
    "tool_timings_ms": {
      "pfz": 0.08,
      "sst": 0.04,
      "chlorophyll": 0.02,
      "restrictions": 11.20,
      "opportunity": 0.49,
      "risk": 0.26,
      "ranking": 0.14,
      "decision": 0.17
    },
    "llm_used": false,
    "llm_fallback": true,
    "llm_fallback_reason": "NETWORK_UNREACHABLE",
    "llm_provider": "gemini",
    "llm_model": "gemini-3.7-flash"
  },

  "disclaimer": "This assessment uses synthetic marine demonstration data for the current prototype. It is a deterministic demonstration heuristic and does not constitute official maritime safety certification, port clearance, or statutory navigation advice."
}
```

---

## 3. Frontend Portal Integration Guide

### For P1 (Fisherman UI)
- **Primary Hero Recommendation**: Render `decision.selected_zone_id` (`ZONE_B`), `decision.distance_nm`, `decision.bearing`, and `decision.species`.
- **Safety Banner**: Bind directly to `decision.safety_level` (`safe_green`, `caution_yellow`, `warning_orange`, `danger_red`) and `decision.action_advice`.
- **Alternative / Rejected Zones Drawer**: Loop over `zones` where `status != "SELECTED"` to show why `ZONE_A` (High Risk) or `ZONE_C` (Sanctuary) were rejected.
- **Metric Badges**: Render `visual_payload.metric_badges`.
- **Chat Transcript**: Display `message` directly in markdown.

### For P2 (Researcher / GIS UI)
- **Map Layer**: Feed `visual_payload.map_features_geojson` directly into MapLibre / Leaflet GeoJSON layer. Auto-center on `visual_payload.focus_zone_id`.
- **Forecast Charts**: Plot `visual_payload.charts_data` (wave height, wind speed vs time).
- **Zone Comparison Table**: Render `zones` array as a tabular matrix comparing Opportunity, Marine Risk, Regulatory Clearance, and Ranking Score across all evaluated coordinates.
- **Evidence & Provenance Drawer**: Expand `evidence` items to show raw metrics, sensor source tags, and timestamps.
- **Performance Inspector**: Display `telemetry.total_pipeline_ms` and per-node / per-tool latencies in developer telemetry drawers.

---

## 4. Running Backend Locally

To start the unified FastAPI server (handling both `/chat` and `/p5/v1/*`):

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8105 --reload
```

Frontend portals configured with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8105` will immediately connect and function with live agent telemetry.
