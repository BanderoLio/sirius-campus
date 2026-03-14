from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from typing import Optional
from uuid import UUID
from datetime import date

from src.dependencies.auth import get_current_user, require_educator_or_admin
from src.dependencies.services import get_duty_schedule_service
from src.grpc_clients.auth_client import AuthenticatedUser
from src.request_audit import write_request_audit
from src.schemas import (
    DutyScheduleResponse,
    DutyScheduleCreate,
    DutyScheduleUpdate,
    DutySchedulePatch,
    DutyScheduleListResponse,
)
from src.services.duty_schedule_service import DutyScheduleService

router = APIRouter(prefix="/duties/schedules", tags=["Duty Schedules"])


@router.get("", response_model=DutyScheduleListResponse)
async def get_schedules(
    background_tasks: BackgroundTasks,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    room_id: Optional[UUID] = None,
    duty_date_from: Optional[date] = None,
    duty_date_to: Optional[date] = None,
    status: Optional[str] = None,
    service: DutyScheduleService = Depends(get_duty_schedule_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    schedules, total = await service.list(
        current_user=current_user,
        page=page,
        size=size,
        room_id=room_id,
        duty_date_from=duty_date_from,
        duty_date_to=duty_date_to,
        status=status,
    )

    pages = (total + size - 1) // size if total > 0 else 0
    background_tasks.add_task(
        write_request_audit,
        "/api/v1/duties/schedules",
        str(room_id) if room_id else None,
        str(current_user.user_id),
    )

    return DutyScheduleListResponse(
        items=[DutyScheduleResponse.model_validate(s) for s in schedules],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=DutyScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    background_tasks: BackgroundTasks,
    schedule_data: DutyScheduleCreate,
    service: DutyScheduleService = Depends(get_duty_schedule_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    schedule = await service.create(
        current_user=current_user,
        room_id=schedule_data.room_id,
        duty_date=schedule_data.duty_date,
    )
    background_tasks.add_task(
        write_request_audit,
        "/api/v1/duties/schedules",
        str(schedule.id),
        str(current_user.user_id),
    )
    return DutyScheduleResponse.model_validate(schedule)


@router.get("/{schedule_id}", response_model=DutyScheduleResponse)
async def get_schedule(
    background_tasks: BackgroundTasks,
    schedule_id: UUID,
    service: DutyScheduleService = Depends(get_duty_schedule_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    schedule = await service.get(current_user=current_user, schedule_id=schedule_id)
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/schedules/{schedule_id}",
        str(schedule_id),
        str(current_user.user_id),
    )

    return DutyScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=DutyScheduleResponse)
async def update_schedule(
    background_tasks: BackgroundTasks,
    schedule_id: UUID,
    schedule_data: DutyScheduleUpdate,
    service: DutyScheduleService = Depends(get_duty_schedule_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    schedule = await service.update(
        schedule_id=schedule_id,
        room_id=schedule_data.room_id,
        duty_date=schedule_data.duty_date,
        status=schedule_data.status,
    )
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/schedules/{schedule_id}",
        str(schedule_id),
        str(current_user.user_id),
    )

    return DutyScheduleResponse.model_validate(schedule)


@router.patch("/{schedule_id}", response_model=DutyScheduleResponse)
async def patch_schedule(
    background_tasks: BackgroundTasks,
    schedule_id: UUID,
    schedule_data: DutySchedulePatch,
    service: DutyScheduleService = Depends(get_duty_schedule_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    schedule = await service.patch(schedule_id=schedule_id, status=schedule_data.status)
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/schedules/{schedule_id}",
        str(schedule_id),
        str(current_user.user_id),
    )

    return DutyScheduleResponse.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    background_tasks: BackgroundTasks,
    schedule_id: UUID,
    service: DutyScheduleService = Depends(get_duty_schedule_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    await service.delete(schedule_id=schedule_id)
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/schedules/{schedule_id}",
        str(schedule_id),
        str(current_user.user_id),
    )
