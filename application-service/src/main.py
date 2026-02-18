import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.v1.applications.routers import router as applications_router
from src.config import settings
from src.database import engine
from src.exceptions import register_exception_handlers
from src.middleware.tracing import TracingMiddleware

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level.upper(), logging.INFO)
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

app = FastAPI(
    title="Application Service",
    description="Exit applications module (Кампус Сириус)",
    version="0.1.0",
)

app.add_middleware(TracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(applications_router, prefix="/api/v1")


@app.get("/health/liveness")
async def liveness() -> dict:
    return {"status": "ok"}


@app.get("/health/readiness")
async def readiness() -> dict:
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return {"status": "unhealthy", "database": "unavailable"}
    return {"status": "ok", "database": "connected"}
