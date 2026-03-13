from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database import get_db
from src.database.models import DutyCategory
from src.schemas import (
    DutyCategoryResponse,
    DutyCategoryListResponse,
)

router = APIRouter(prefix="/duties/categories", tags=["Duty Report Categories"])


@router.get("", response_model=DutyCategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyCategory)
    
    count_query = select(func.count()).select_from(DutyCategory)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    categories = result.scalars().all()
    
    pages = (total + size - 1) // size if total > 0 else 0
    
    return DutyCategoryListResponse(
        items=[DutyCategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
