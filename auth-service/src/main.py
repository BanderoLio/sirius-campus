"""
Auth Service main application entry point.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router as api_router
from src.core.config import get_settings
from src.core.database import engine
from src.models.database import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create database tables
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    # Start gRPC server in background
    logger.info("Starting gRPC server...")
    grpc_task = asyncio.create_task(start_grpc_server())
    logger.info("gRPC server task created")

    yield

    # Shutdown: Cancel gRPC server
    logger.info("Shutting down gRPC server...")
    grpc_task.cancel()
    try:
        await grpc_task
    except asyncio.CancelledError:
        pass

    # Close database connections
    await engine.dispose()
    logger.info("Application shutdown complete")


async def start_grpc_server():
    """Start gRPC server."""
    from src.grpc_server.auth import serve_grpc

    await serve_grpc()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Auth Service for Campus Sirius",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
