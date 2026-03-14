from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from uuid import UUID

from src.dependencies.auth import get_current_user
from src.dependencies.services import get_duty_image_service
from src.grpc_clients.auth_client import AuthenticatedUser
from src.request_audit import write_request_audit
from src.schemas import (
    DutyReportImageResponse,
)
from src.services.duty_image_service import DutyImageService, upload_image_in_background

router = APIRouter(prefix="/duties/reports/{report_id}/images", tags=["Duty Report Images"])


@router.post("", response_model=DutyReportImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
    background_tasks: BackgroundTasks,
    report_id: UUID,
    category_id: UUID = Form(...),
    file: UploadFile = File(...),
    service: DutyImageService = Depends(get_duty_image_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    payload = await file.read()
    image = await service.create_pending(
        report_id=report_id,
        category_id=category_id,
    )
    background_tasks.add_task(
        upload_image_in_background,
        image.id,
        report_id,
        category_id,
        file.filename or "image",
        file.content_type or "application/octet-stream",
        payload,
    )
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/reports/{report_id}/images",
        str(report_id),
        str(current_user.user_id),
    )

    return DutyReportImageResponse.model_validate(image)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    background_tasks: BackgroundTasks,
    report_id: UUID,
    image_id: UUID,
    service: DutyImageService = Depends(get_duty_image_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    await service.delete(report_id=report_id, image_id=image_id)
    background_tasks.add_task(
        write_request_audit,
        f"/api/v1/duties/reports/{report_id}/images/{image_id}",
        str(image_id),
        str(current_user.user_id),
    )
