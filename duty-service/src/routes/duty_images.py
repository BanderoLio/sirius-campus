from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.database import get_db
from src.database.models import DutyReportImage
from src.schemas import (
    DutyReportImageResponse,
    DutyReportImageCreate,
)

router = APIRouter(prefix="/duties/reports/{report_id}/images", tags=["Duty Report Images"])


@router.post("", response_model=DutyReportImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
    report_id: UUID,
    image_data: DutyReportImageCreate,
    db: AsyncSession = Depends(get_db),
):
    image = DutyReportImage(
        report_id=report_id,
        category_id=image_data.category_id,
        photo_url=image_data.photo_url,
    )
    
    db.add(image)
    await db.commit()
    await db.refresh(image)
    
    return DutyReportImageResponse.model_validate(image)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    report_id: UUID,
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutyReportImage).where(
        DutyReportImage.id == image_id,
        DutyReportImage.report_id == report_id
    )
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    await db.delete(image)
    await db.commit()
