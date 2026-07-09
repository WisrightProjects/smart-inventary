"""FastAPI application entrypoint.

Run with: uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import alerts, analytics, history, inventory, live, products, sync, verify, workers
from backend.config.settings import settings
from backend.utils.logger import get_logger
from database.session import init_db

logger = get_logger("system")

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(live.router, prefix=settings.api_prefix)
app.include_router(verify.router, prefix=settings.api_prefix)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(history.router, prefix=settings.api_prefix)
app.include_router(inventory.router, prefix=settings.api_prefix)
app.include_router(workers.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(sync.router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("%s started", settings.app_name)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
