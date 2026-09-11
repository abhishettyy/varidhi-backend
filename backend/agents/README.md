# Marine Intelligence Platform — Agent Orchestration (P3) & Tools Integration (P4)

This module implements the cognitive orchestration engine (**P3**) and data retrieval tools (**P4**) for the **Agentic AI Marine Intelligence Platform**.

---

## 👥 Architecture & Ownership Boundaries

```text
P3 = WHAT should happen (orchestration, planning, decision)
P4 = HOW data is obtained (retrieval, adapters, normalization)
P6 = HOW data is interpreted (marine risk, opportunity, calculations)
```

```mermaid
flowchart TD
    User([User Natural Language Query]) --> Understand[P3 Query Understanding]
    Understand --> Plan[P3 Planner]
    Plan --> ExecPlan[Structured ExecutionPlan]
    ExecPlan --> TS[P3 Tool Selection]
    TS --> Exec[P3 Generic DAG Executor]
    
    subgraph Registry Layer
        Exec --> Registry[Tool Registry]
    end
    
    subgraph P4 Data Tools
        Registry --> P4_PFZ[get_pfz]
        Registry --> P4_SST[get_sst]
        Registry --> P4_CHL[get_chlorophyll]
        Registry --> P4_WIND[get_wind]
        Registry --> P4_WAVE[get_wave]
        Registry --> P4_SWELL[get_swell]
        Registry --> P4_TIDE[get_tide]
        Registry --> P4_CURR[get_currents]
        Registry --> P4_RESTR[check_restrictions]
    end
    
    subgraph P6 Analytics & Decision
        Registry --> P6_OPP[calculate_opportunity]
        Registry --> P6_RISK[calculate_marine_risk]
        Registry --> P6_RANK[rank_zones]
        Registry --> P3_DEC[select_safe_fishing_zone]
    end
    
    P4_PFZ & P4_SST & P4_CHL --> P6_OPP
    P4_WIND & P4_WAVE & P4_SWELL & P4_TIDE --> P6_RISK
    P6_OPP & P6_RISK --> P6_RANK
    P6_RANK & P4_RESTR --> P3_DEC
    
    P3_DEC --> RespGen[P3 Response Generation]
    RespGen --> FinalResp([Structured AgentResponse & VisualPayload])
```

---

## 📦 Canonical Tool Result Contract (P4)

Every P4 tool conforms to the standardized envelope schema:

```python
{
    "status": "success",          # "success" | "partial" | "unavailable" | "error" | "failed"
    "source": "synthetic",        # "synthetic" | "INCOIS" | "Open-Meteo" | "Copernicus"
    "operation": "get_sst",       # Canonical operation name
    "observation_time": "...",    # ISO 8601 observation/satellite timestamp (or None)
    "valid_time": "...",          # ISO 8601 forecast validity timestamp (or None)
    "data": { ... },              # Normalized domain data
    "quality": "high",            # Data quality descriptor
    "metadata": { ... }           # Technical dataset provenance
}
```

### Time Semantics Contract
- **Satellite / Observation Tools** (`get_sst`, `get_chlorophyll`, `get_pfz`): Use `latest_available` temporal mode. Populates `observation_time`, while `valid_time` is `None`.
- **Forecast Tools** (`get_wind`, `get_wave`, `get_swell`, `get_tide`, `get_currents`): Use `forecast` temporal mode. Populates `valid_time`.

---

## 🛠️ Implemented P4 Tools

| Tool Operation | Data Provided | Temporal Mode | Source Label |
| :--- | :--- | :--- | :--- |
| `get_pfz` | Multi-zone coordinates, bearing, distance, species | `latest_available` | `synthetic` |
| `get_sst` | Mean SST, thermal gradient (°C/km), thermal fronts | `latest_available` | `synthetic` |
| `get_chlorophyll` | Chlorophyll-a density ($mg/m^3$), productivity proxy | `latest_available` | `synthetic` |
| `get_wind` | Speed (knots/m/s), direction, gusts | `forecast` | `synthetic` |
| `get_wave` | Significant wave height ($H_s$), period, direction | `forecast` | `synthetic` |
| `get_swell` | Swell height ($m$), period ($s$), direction | `forecast` | `synthetic` |
| `get_tide` | Tide phase (flood/ebb), water level ($m$), tide times | `forecast` | `synthetic` |
| `get_currents` | Current velocity (knots), direction | `forecast` | `synthetic` |
| `check_restrictions` | Marine protected areas, port security, ban zones | N/A | `synthetic` |

---

## 🔌 Swapping Between Mock and P4 Tools

The generic P3 DAG executor works transparently with both mock tools and P4 tools:

```python
from backend.agents.tools import use_p4_tools, use_mock_tools

# Switch to P4 tools
use_p4_tools()

# Switch to mock tools
use_mock_tools()
```

---

## 🧪 Testing

Run the full test suite (90 tests):

```bash
python -m unittest discover -s backend
```
