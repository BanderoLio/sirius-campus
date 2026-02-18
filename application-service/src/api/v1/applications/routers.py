from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, status, UploadFile

from src.api.v1.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationDecideRequest,
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationResponse,
    DocumentResponse,
)
from src.dependencies import (
    get_application_service,
    get_current_user,
)
from src.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


def _to_response(model: object) -> ApplicationResponse:
    return ApplicationResponse.model_validate(model)


def _to_detail_response(model: object) -> ApplicationDetailResponse:
    return ApplicationDetailResponse.model_validate(model)


def _to_document_response(model: object) -> DocumentResponse:
    return DocumentResponse.model_validate(model)


@router.get(
    "",
    response_model=ApplicationListResponse,
    summary="List applications",
)
async def list_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    user_id, roles = current_user
    is_educator = any(
        r in roles for r in ("educator", "educator_head", "admin")
    )
    filter_user_id = None if is_educator else user_id
    items, total = await service.list_applications(
        user_id=filter_user_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        page=page,
        size=size,
    )
    pages = (total + size - 1) // size if total else 0
    return ApplicationListResponse(
        items=[_to_response(m) for m in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create application",
)
async def create_application(
    body: ApplicationCreateRequest,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    user_id, _ = current_user
    model, _ = await service.create_application(
        user_id=user_id,
        leave_time=body.leave_time,
        return_time=body.return_time,
        reason=body.reason,
        contact_phone=body.contact_phone,
    )
    return _to_response(model)


@router.get(
    "/{application_id}",
    response_model=ApplicationDetailResponse,
    summary="Get application by ID",
)
async def get_application(
    application_id: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    user_id, roles = current_user
    app = await service.get_application(
        application_id=application_id,
        current_user_id=user_id,
        current_user_roles=roles,
    )
    return _to_detail_response(app)


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse,
    summary="Approve or reject application",
)
async def decide_application(
    application_id: UUID,
    body: ApplicationDecideRequest,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    user_id, roles = current_user
    is_educator = any(
        r in roles for r in ("educator", "educator_head", "admin")
    )
    if not is_educator:
        from src.domain.exceptions import ForbiddenApplicationError

        raise ForbiddenApplicationError()
    updated = await service.decide_application(
        application_id=application_id,
        status=body.status,
        decided_by=user_id,
        decided_at=datetime.now(timezone.utc),
        reject_reason=body.reject_reason,
    )
    return _to_response(updated)


@router.post(
    "/{application_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
)
async def upload_document(
    application_id: UUID,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
):
    user_id, _ = current_user
    data = await file.read()
    content_type = file.content_type or "application/octet-stream"
    filename = file.filename or "file"
    doc = await service.upload_document(
        application_id=application_id,
        document_type=document_type,
        file_data=data,
        content_type=content_type,
        filename=filename,
        uploaded_by=user_id,
    )
    return _to_document_response(doc)
