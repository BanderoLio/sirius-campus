from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database import engine, Base
from src.routes import (
    schedules_router,
    reports_router,
    images_router,
    categories_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Duty Service API",
    description="Микросервис управления дежурствами в Кампусе Сириус",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(schedules_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "duty-service",
        "version": "1.0.0"
    }
