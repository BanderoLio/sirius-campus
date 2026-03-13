from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from uuid import UUID
from datetime import date

from src.database import get_db
from src.database.models import DutySchedule, DutyStatusEnum
from src.schemas import (
    DutyScheduleResponse,
    DutyScheduleCreate,
    DutyScheduleUpdate,
    DutySchedulePatch,
    DutyScheduleListResponse,
)

router = APIRouter(prefix="/duties/schedules", tags=["Duty Schedules"])


@router.get("", response_model=DutyScheduleListResponse)
async def get_schedules(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    room_id: Optional[UUID] = None,
    duty_date_from: Optional[date] = None,
    duty_date_to: Optional[date] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutySchedule)
    
    if room_id:
        query = query.where(DutySchedule.room_id == room_id)
    if duty_date_from:
        query = query.where(DutySchedule.duty_date >= duty_date_from)
    if duty_date_to:
        query = query.where(DutySchedule.duty_date <= duty_date_to)
    if status:
        query = query.where(DutySchedule.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    schedules = result.scalars().all()
    
    pages = (total + size - 1) // size if total > 0 else 0
    
    return DutyScheduleListResponse(
        items=[DutyScheduleResponse.model_validate(s) for s in schedules],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=DutyScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_data: DutyScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    assigned_by = UUID("550e8400-e29b-41d4-a716-446655440300")
    
    schedule = DutySchedule(
        room_id=schedule_data.room_id,
        duty_date=schedule_data.duty_date,
        assigned_by=assigned_by,
        status=DutyStatusEnum.pending,
    )
    
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    
    return DutyScheduleResponse.model_validate(schedule)


@router.get("/{schedule_id}", response_model=DutyScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutySchedule).where(DutySchedule.id == schedule_id)
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return DutyScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=DutyScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    schedule_data: DutyScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutySchedule).where(DutySchedule.id == schedule_id)
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.room_id = schedule_data.room_id
    schedule.duty_date = schedule_data.duty_date
    schedule.status = schedule_data.status
    
    await db.commit()
    await db.refresh(schedule)
    
    return DutyScheduleResponse.model_validate(schedule)


@router.patch("/{schedule_id}", response_model=DutyScheduleResponse)
async def patch_schedule(
    schedule_id: UUID,
    schedule_data: DutySchedulePatch,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutySchedule).where(DutySchedule.id == schedule_id)
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule_data.status:
        schedule.status = schedule_data.status
    
    await db.commit()
    await db.refresh(schedule)
    
    return DutyScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    query = select(DutySchedule).where(DutySchedule.id == schedule_id)
    result = await db.execute(query)
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await db.delete(schedule)
    await db.commit()
