# Varidhi — Agentic Marine Intelligence Platform

> **SIH 2026 Project** · Smart India Hackathon  
> *Evidence-grounded, deterministic AI advisory for coastal fishing communities, maritime authorities, and oceanographic researchers.*

---

## What is Varidhi?

**Varidhi** is a full-stack, multi-persona agentic AI platform that helps fishermen, marine authorities, and researchers make safe, data-driven decisions about coastal and offshore marine activity.

A natural language query like:
> *"I'm near Mangalore. Where should I fish tomorrow morning?"*

triggers a complete intelligence pipeline:
1. **LLM-powered query understanding** (Gemini / OpenAI)  
2. **Deterministic oceanographic tool execution** — PFZ, SST, wave, wind, current, tide, restrictions  
3. **P6 deterministic analytics** — Opportunity scoring, Marine Risk scoring, Regulatory gate  
4. **Ranked zone decision** — Zone B selected, Zone A rejected (high risk), Zone C rejected (MPA)  
5. **Structured, evidence-grounded response** with GIS visual payload

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND  (Next.js 16 / TypeScript)         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │  P1 Fisherman    │  │ P2 Researcher /  │  │ Maritime Authority │  │
│  │  Advisory UI     │  │  GIS Workspace   │  │ Operations Center  │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────┘  │
│         ↕ POST /chat · GET /health · GET /p5/v1/*                   │
└─────────────────────────────────────────────────────────────────────┘
                                  ↕ HTTP (port 8105)
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND  (FastAPI · Python)                       │
│                                                                      │
│  POST /chat ─→  LangGraph Swarm Pipeline                            │
│                   ↓ understand_query                                 │
│                   ↓ planner                                          │
│                   ↓ tool_selection                                   │
│                   ↓ executor  ←─── P4 Marine Tools (9 tools)        │
│                   ↓ evidence_assembly                                │
│                   ↓ response_generation  ←── P6 Analytics Engine    │
│                   ↓                                                  │
│               ChatResponse (JSON)                                    │
│                                                                      │
│  GET /p5/v1/*  ── P5 Data Service (zones, PFZ, wave, SST, ...)      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Team & Module Ownership

| Module | Owner | Responsibility |
|--------|-------|----------------|
| **P1** | Frontend Team | Fisherman Advisory UI (`/fisherman`) |
| **P2** | Frontend Team | Researcher / GIS Workspace (`/researcher`) |
| **P3** | Agent Team | LangGraph orchestration, planning, response generation |
| **P4** | Tools Team | Marine data retrieval tools, adapters, normalization |
| **P5** | Data Team | INCOIS / ocean data ingestion, `/p5/v1/*` REST API |
| **P6** | Analytics Team | Opportunity scoring, Marine Risk, decision engine |

---

## Key Features

- 🧠 **Real LLM Integration** — Gemini (primary) / OpenAI (secondary) / Deterministic fallback
- 🎯 **Deterministic Decision Engine (P6)** — No LLM hallucination on numerical results
- 🗺️ **GIS Visual Payload** — MapLibre GL map with zone layers, PFZ, restrictions, weather
- 👤 **Multi-persona Advisory** — Tailored responses for fishermen, researchers, and authorities
- 📡 **INCOIS PFZ Integration** — Potential Fishing Zone satellite composite data
- ⚡ **LangGraph Swarm** — Async multi-node pipeline with full telemetry
- 🧪 **255 Backend Tests** — Full unit + integration test coverage

---

## Canonical Mangalore Scenario (Phase 5B / 6 Fixture)

| Zone | Coordinates | Opportunity | Risk | Rank | Distance | Status |
|------|-------------|-------------|------|------|----------|--------|
| **Zone B** | 12.90°N, 74.95°E | 66.9 | 34.9 | **67.31** | 8.2 NM SSW | ✅ **SELECTED** |
| Zone A | 12.95°N, 74.80°E | 76.6 | 75.2 | — | 14.5 NM WNW | ❌ Risk > 50 |
| Zone C | 12.82°N, 75.05°E | 84.5 | 30.8 | — | 18.0 NM SSE | ❌ Inside MPA |

---

## Project Structure

```
Varidhi/
├── backend/
│   ├── main.py                   # FastAPI entrypoint
│   ├── requirements.txt
│   ├── agents/                   # P3 LangGraph orchestration
│   │   ├── graph/                # LangGraph node definitions
│   │   ├── nodes/                # understand_query, planner, executor, ...
│   │   ├── tools/                # P4 marine data tools
│   │   ├── analytics/            # P6 opportunity/risk/decision engine
│   │   ├── llm/                  # LLM providers (Gemini, OpenAI, Fake)
│   │   ├── schemas/              # Pydantic models
│   │   └── tests/                # 255 unit + integration tests
│   ├── api/                      # FastAPI routes & schemas
│   │   ├── routes.py             # POST /chat, GET /health
│   │   └── schemas.py            # ChatRequest, ChatResponse
│   └── p5/                       # P5 data service
│       └── api.py                # GET /p5/v1/zones, /pfz, /wave, /sst, ...
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Landing portal
│   │   ├── fisherman/page.tsx    # P1 Fisherman workspace
│   │   ├── researcher/page.tsx   # P2 Researcher GIS workspace
│   │   └── authority/page.tsx    # Maritime authority operations
│   ├── components/
│   │   ├── chat/                 # ChatPanel, AIResponseCard, EvidencePanel
│   │   ├── fisherman/            # RecommendationCard, FishermanMap, ...
│   │   ├── researcher/           # ZoneDetailDrawer, OceanTimeSeries, ...
│   │   ├── authority/            # AuthorityMap, AlertPanel, ...
│   │   └── map/                  # MarineMap, ZoneLayer, PFZLayer, ...
│   ├── services/api/
│   │   ├── chatApi.ts            # POST /chat integration
│   │   ├── marineApi.ts          # GET /p5/v1/* integration
│   │   └── client.ts             # Base API client
│   ├── types/
│   │   ├── chat.ts               # AgentResponseData, DecisionSummary, ...
│   │   └── marine.ts             # FishingZone, RoleType, SafetySeverity
│   └── data/mock/                # Canonical fallback fixtures
│
├── docs/
│   └── API_CONTRACT_P1_P2.md     # Backend ↔ Frontend API contract
│
├── run_marine_query.py            # CLI telemetry runner
└── .env.example                   # Environment variable template
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

---

### 1. Clone & Configure Environment

```bash
git clone <repo-url>
cd Varidhi
cp .env.example .env
```

Edit `.env` and add your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
# Optional:
# OPENAI_API_KEY=your_openai_api_key_here
```

---

### 2. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

---

### 3. Start the Backend

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8105 --reload
```

The API is now available at `http://127.0.0.1:8105`.

**Verify health:**
```bash
curl http://127.0.0.1:8105/health
```
```json
{ "status": "ok", "service": "Varidhi Marine Intelligence API", "llm_provider": "GEMINI" }
```

---

### 4. Install & Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Open your browser at `http://localhost:3000`.

---

### 5. Run a Query via CLI

```bash
python run_marine_query.py "I'm near Mangalore. Where should I fish tomorrow morning?" --role fisherman
```

---

## API Reference

Full contract documented in [`docs/API_CONTRACT_P1_P2.md`](docs/API_CONTRACT_P1_P2.md).

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Submit a natural language marine query |
| `GET` | `/health` | Liveness check + LLM provider status |
| `GET` | `/p5/v1/zones` | Candidate zone spatial metadata |
| `GET` | `/p5/v1/pfz` | Potential Fishing Zone composite data |
| `GET` | `/p5/v1/wave` | Wave & swell forecast |
| `GET` | `/p5/v1/wind` | Wind speed & direction forecast |
| `GET` | `/p5/v1/sst` | Sea Surface Temperature |
| `GET` | `/p5/v1/restrictions` | Marine protected areas & bans |

### Example Request

```bash
curl -X POST http://127.0.0.1:8105/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Where should I fish tomorrow?", "role": "fisherman"}'
```

### Example Response (abridged)

```json
{
  "decision": {
    "selected_zone_id": "ZONE_B",
    "status": "SELECTED",
    "opportunity_score": 66.9,
    "risk_score": 34.9,
    "ranking_score": 67.31,
    "regulatory_status": "ELIGIBLE",
    "distance_nm": 8.2,
    "bearing": "SSW",
    "species": ["Mackerel", "Sardines"],
    "action_advice": "Favorable relative to evaluated alternatives. Maintain standard maritime vigilance."
  },
  "zones": [ ... ],
  "evidence": [ ... ],
  "visual_payload": {
    "focus_zone_id": "ZONE_B",
    "metric_badges": { "Opportunity": "66.9/100", "Risk": "34.9/100", "Rank": "67.31/100" }
  },
  "telemetry": {
    "total_pipeline_ms": 1240,
    "llm_provider": "GEMINI",
    "parser_mode": "LLM"
  },
  "disclaimer": "Advisory generated using synthetic INCOIS data for demonstration purposes."
}
```

---

## Running Tests

```bash
# Full backend test suite (255 tests)
python -m unittest discover -s backend/agents/tests -p "test_*.py"
```

Expected output:
```
Ran 255 tests in ~65s
OK
```

---

## LLM Provider Configuration

Set in `.env`:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (primary) |
| `OPENAI_API_KEY` | OpenAI API key (secondary fallback) |

If no API key is configured, the system automatically falls back to the deterministic rule-based parser — **all P6 numerical scores remain identical regardless of LLM provider**.

---

## Frontend Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8105
```

---

## LangGraph Pipeline

```
START
  ↓
understand_query      ← LLM: entity extraction, intent classification
  ↓
planner               ← LLM: tool selection plan
  ↓
tool_selection        ← Deterministic: maps plan → P4 tool calls
  ↓
executor              ← Async: runs P4 tools, feeds P6 analytics
  ↓
evidence_assembly     ← Deterministic: packages tool results
  ↓
response_generation   ← LLM: formats natural language response
  ↓
END  →  ChatResponse (decision + zones + evidence + visual_payload + telemetry)
```

**Invariant:** LLM never influences zone selection, risk scores, opportunity scores, or regulatory decisions. The **P6 Deterministic Decision Engine is always authoritative**.

---

## Portals

| Portal | URL | Persona |
|--------|-----|---------|
| Landing | `http://localhost:3000` | All |
| Fisherman Advisory | `http://localhost:3000/fisherman` | Fisherman |
| Researcher / GIS | `http://localhost:3000/researcher` | Oceanographer |
| Maritime Authority | `http://localhost:3000/authority` | Coast Guard / Port Authority |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, MapLibre GL |
| Backend | FastAPI, Python 3.11, LangGraph 0.2, LangChain Core |
| LLM | Google Gemini (primary), OpenAI (fallback), Deterministic (default) |
| Analytics | Custom P6 deterministic engine (no ML) |
| Maps | MapLibre GL JS (open-source, no API key required) |
| Data | Synthetic INCOIS PFZ + Open-Meteo + Copernicus structure |

---

## Branch

Active development branch: `p3/langraph-integration`

---

*Built for Smart India Hackathon 2026 — Varidhi Marine Intelligence Platform*
