import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import LOKI_URL
from app.routers import applications

# Logging: console always; Loki when LOKI_URL is set
_root = logging.getLogger()
_root.setLevel(logging.INFO)
_root.handlers.clear()
_root.addHandler(logging.StreamHandler(sys.stdout))
if LOKI_URL:
    try:
        from logging_loki import LokiHandler

        _root.addHandler(
            LokiHandler(
                url=f"{LOKI_URL.rstrip('/')}/loki/api/v1/push",
                tags={"service": "gateway"},
                version="1",
            )
        )
    except Exception:  # noqa: BLE001
        pass

app = FastAPI(
    title="Campus Gateway BFF",
    description="Single REST entry point; backend services are called via gRPC.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health/liveness")
def health_liveness():
    return "ok"


app.include_router(applications.router, prefix="/api/v1")
