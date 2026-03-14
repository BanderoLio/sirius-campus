from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from typing import Optional
from uuid import UUID

from src.dependencies.auth import get_current_user, require_educator_or_admin
from src.dependencies.services import get_duty_report_service
from src.grpc_clients.auth_client import AuthenticatedUser
from src.request_audit import write_request_audit
from src.schemas import (
    DutyReportResponse,
    DutyReportCreate,
    DutyReportUpdate,
    DutyReportPatch,
    DutyReportListResponse,
    DutyReportDetailResponse,
)
from src.services.duty_report_service import DutyReportService

router = APIRouter(prefix="/duties/reports", tags=["Duty Reports"])


@router.get("", response_model=DutyReportListResponse)
async def get_reports(
    background_tasks: BackgroundTasks,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    schedule_id: Optional[UUID] = None,
    status: Optional[str] = None,
    service: DutyReportService = Depends(get_duty_report_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    reports, total = await service.list(
        current_user=current_user,
        page=page,
        size=size,
        schedule_id=schedule_id,
        status=status,
    )

    pages = (total + size - 1) // size if total > 0 else 0
    background_tasks.add_task(
        write_request_audit,
        "/api/v1/duties/reports",
        str(schedule_id) if schedule_id else None,
        str(current_user.user_id),
    )

    return DutyReportListResponse(
        items=[DutyReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=DutyReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    background_tasks: BackgroundTasks,
    report_data: DutyReportCreate,
    service: DutyReportService = Depends(get_duty_report_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    report = await service.create(current_user=current_user, schedule_id=report_data.schedule_id)
    background_tasks.add_task(
        write_request_audit,
        "/api/v1/duties/reports",
        str(report.id),
        str(current_user.user_id),
    )

    return DutyReportResponse.model_validate(report)


@router.get("/{report_id}", response_model=DutyReportDetailResponse)
async def get_report(
    background_tasks: BackgroundTasks,
    report_id: UUID,
    service: DutyReportService = Depends(get_duty_report_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    report = await service.get(current_user=current_user, report_id=report_id)
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/reports/{report_id}",
        str(report_id),
        str(current_user.user_id),
    )

    return DutyReportDetailResponse.model_validate(report)


@router.put("/{report_id}", response_model=DutyReportResponse)
async def update_report(
    background_tasks: BackgroundTasks,
    report_id: UUID,
    report_data: DutyReportUpdate,
    service: DutyReportService = Depends(get_duty_report_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    report = await service.update(
        report_id=report_id,
        schedule_id=report_data.schedule_id,
        status=report_data.status,
    )
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/reports/{report_id}",
        str(report_id),
        str(current_user.user_id),
    )

    return DutyReportResponse.model_validate(report)


@router.patch("/{report_id}", response_model=DutyReportResponse)
async def patch_report(
    background_tasks: BackgroundTasks,
    report_id: UUID,
    report_data: DutyReportPatch,
    service: DutyReportService = Depends(get_duty_report_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    report = await service.patch(
        current_user=current_user,
        report_id=report_id,
        status=report_data.status,
        reject_reason=report_data.reject_reason,
    )
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/reports/{report_id}",
        str(report_id),
        str(current_user.user_id),
    )

    return DutyReportResponse.model_validate(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    background_tasks: BackgroundTasks,
    report_id: UUID,
    service: DutyReportService = Depends(get_duty_report_service),
    current_user: AuthenticatedUser = Depends(require_educator_or_admin),
):
    await service.delete(report_id=report_id)
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/reports/{report_id}",
        str(report_id),
        str(current_user.user_id),
    )
