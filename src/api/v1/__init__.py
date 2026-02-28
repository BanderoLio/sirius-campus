"""
API v1 router.
"""
from fastapi import APIRouter

from src.api.v1.auth import router as auth_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router, prefix="/auth")
