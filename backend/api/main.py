"""FastAPI Application Entrypoint for Varidhi Marine Intelligence Platform (Phase 8).

Run backend server:
    uvicorn backend.api.main:app --host 127.0.0.1 --port 8105 --reload
or:
    uvicorn backend.main:app --port 8105
"""

import os
import sys
from typing import List

_vendor_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vendor"))
if os.path.isdir(_vendor_dir) and _vendor_dir not in sys.path:
    sys.path.insert(0, _vendor_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as agent_router
from backend.p5.api import create_app as create_p5_app

DEFAULT_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:8105",
    "http://127.0.0.1:8105",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


def get_cors_origins() -> List[str]:
    """Retrieve allowed CORS origins from environment or default dev ports."""
    env_origins = os.environ.get("CORS_ORIGINS")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return DEFAULT_CORS_ORIGINS


def create_app() -> FastAPI:
    """Factory creating the unified Varidhi Marine Intelligence Platform FastAPI application."""
    app = FastAPI(
        title="Varidhi Marine Intelligence Platform API",
        version="1.0.0",
        description=(
            "Minimal, stable HTTP API providing persona-tailored agentic marine advisories (P3/P6) "
            "and normalized coastal oceanographic data services (P5)."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. CORS Configuration for P1 / P2 frontend portals
    allowed_origins = get_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Register Phase 8 Agent Endpoints (/chat, /health, /api/chat/query)
    app.include_router(agent_router)

    # 3. Register P5 Marine Data Service routes (/p5/v1/*)
    p5_app = create_p5_app()
    for route in p5_app.routes:
        # Avoid duplicate /docs or openapi internal routes
        if hasattr(route, "path") and route.path.startswith("/p5/v1"):
            app.routes.append(route)

    return app


app = create_app()
