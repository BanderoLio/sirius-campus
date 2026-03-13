from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.v1.bookings.routers import router as bookings_router
from src.api.v1.coworkings.routers import router as coworkings_router
from src.config import settings
from src.exceptions import register_exception_handlers
from src.logging_config import configure_logging
from src.middleware.tracing import TracingMiddleware

_log_listener = configure_logging(
    service_name=settings.app_name,
    log_level=settings.log_level,
    loki_url=settings.loki_url,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    _log_listener.stop()


_bearer = HTTPBearer(auto_error=False)

app = FastAPI(
    title="Coworking Service",
    description=(
        "Coworking module (Sirius-Campus)\n\n"
        "**Dev-токены:** `student:dev`, `educator:dev`, `admin:dev`"
    ),
    swagger_ui_parameters={"persistAuthorization": True},
    dependencies=[Depends(_bearer)],
    lifespan=lifespan,
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
