from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from uuid import UUID

from src.dependencies.auth import get_current_user
from src.dependencies.services import get_duty_image_service
from src.grpc_clients.auth_client import AuthenticatedUser
from src.schemas import (
    DutyReportImageResponse,
)
from src.services.duty_image_service import DutyImageService

router = APIRouter(prefix="/duties/reports/{report_id}/images", tags=["Duty Report Images"])


@router.post("", response_model=DutyReportImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(
    report_id: UUID,
    category_id: UUID = Form(...),
    file: UploadFile = File(...),
    service: DutyImageService = Depends(get_duty_image_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    payload = await file.read()
    image = await service.create(
        report_id=report_id,
        category_id=category_id,
        filename=file.filename or "image",
        content_type=file.content_type or "application/octet-stream",
        payload=payload,
    )

    return DutyReportImageResponse.model_validate(image)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    report_id: UUID,
    image_id: UUID,
    service: DutyImageService = Depends(get_duty_image_service),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    await service.delete(report_id=report_id, image_id=image_id)
