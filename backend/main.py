"""Top-level FastAPI runner entrypoint for Varidhi Marine Intelligence Platform.

Usage:
    uvicorn backend.main:app --host 127.0.0.1 --port 8105 --reload
"""

from backend.api.main import app, create_app

__all__ = ["app", "create_app"]
