from fastapi import APIRouter
from src.api.v1.patrols import router as patrols_router

api_router = APIRouter()
api_router.include_router(patrols_router)

__all__ = ["api_router"]
