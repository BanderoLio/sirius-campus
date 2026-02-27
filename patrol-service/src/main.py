import logging
import sys

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager

from src.config import settings
from src.api.v1 import api_router
from src.exceptions import register_exception_handlers
from src.middleware import TracingMiddleware

# Logging: console always; Loki when LOKI_URL is set
log_handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
if getattr(settings, "loki_url", None) and settings.loki_url.strip():
    try:
        from logging_loki import LokiHandler

        log_handlers.append(
            LokiHandler(
                url=f"{settings.loki_url.rstrip('/')}/loki/api/v1/push",
                tags={"service": getattr(settings, "app_name", "patrol-service")},
                version="1",
            )
        )
    except Exception:  # noqa: BLE001
        pass

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(message)s",
    handlers=log_handlers,
)

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
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No gRPC server needed for patrol-service (it's a REST API service)
    yield


app = FastAPI(
    title="Patrol Service API",
    description="Микросервис обходов проекта «Кампус Сириус».",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TracingMiddleware)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health/liveness")
async def liveness() -> dict:
    return {"status": "ok"}


@app.get("/health/readiness")
async def readiness() -> dict:
    from src.database import engine
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return {"status": "unhealthy", "database": "unavailable"}
    return {"status": "ok", "database": "connected"}
