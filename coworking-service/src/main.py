import logging

import structlog
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.v1.bookings.routers import router as bookings_router
from src.api.v1.coworkings.routers import router as coworkings_router
from src.config import settings
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

_bearer = HTTPBearer(auto_error=False)

app = FastAPI(
    title="Coworking Service",
    description=(
        "Coworking space management module (Sirius-Campus)\n\n"
        "**Dev-токены:** `student:dev`, `educator:dev`, `admin:dev`"
    ),
    swagger_ui_parameters={"persistAuthorization": True},
    dependencies=[Depends(_bearer)],
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

app.include_router(coworkings_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")


@app.get("/health/liveness")
async def liveness() -> dict:
    return {"status": "ok"}


@app.get("/health/readiness")
async def readiness() -> dict:
    if settings.use_mocks:
        return {"status": "ok", "database": "mocks"}
    from sqlalchemy import text
    from src.database import get_engine

    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return {"status": "unhealthy", "database": "unavailable"}
    return {"status": "ok", "database": "connected"}
