from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import get_current_user
from src.dependencies.services import get_duty_category_service
from src.grpc_clients.auth_client import AuthenticatedUser
from src.schemas import (
    DutyCategoryResponse,
    DutyCategoryListResponse,
)
from src.services.duty_category_service import DutyCategoryService

router = APIRouter(prefix="/duties/categories", tags=["Duty Report Categories"])


@router.get("", response_model=DutyCategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    service: DutyCategoryService = Depends(get_duty_category_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    categories, total = await service.list(page=page, size=size)

    pages = (total + size - 1) // size if total > 0 else 0

    return DutyCategoryListResponse(
        items=[DutyCategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
