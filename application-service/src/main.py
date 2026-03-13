import logging
import sys

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager

from src.config import settings
from src.grpc_server.server import create_and_start_grpc_server

# Logging: console always; Loki when LOKI_URL is set
log_handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
if getattr(settings, "loki_url", None) and settings.loki_url.strip():
    try:
        from logging_loki import LokiHandler

        log_handlers.append(
            LokiHandler(
                url=f"{settings.loki_url.rstrip('/')}/loki/api/v1/push",
                tags={"service": getattr(settings, "app_name", "application-service")},
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
    grpc_server = await create_and_start_grpc_server()
    try:
        yield
    finally:
        if grpc_server is not None:
            await grpc_server.stop(grace=5)


app = FastAPI(
    title="Application Service",
    description="Exit applications module (gRPC only); REST is at Gateway BFF.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


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
