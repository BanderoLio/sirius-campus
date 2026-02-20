from datetime import date

import grpc
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile, status

from app.auth_stub import get_user_from_authorization
from app.grpc_client import (
    create_application as grpc_create,
    decide_application as grpc_decide,
    delete_document as grpc_delete_document,
    get_application as grpc_get,
    get_channel,
    get_document_download_url as grpc_get_download_url,
    list_applications as grpc_list,
    upload_document as grpc_upload,
)
from app.grpc_to_http import (
    grpc_error_to_http,
    proto_application_to_response,
    proto_detail_to_response,
    proto_document_to_response,
)
from app.schemas import (
    ApplicationCreateRequest,
    ApplicationDecideRequest,
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationResponse,
    DocumentDownloadResponse,
    DocumentResponse,
)

router = APIRouter(prefix="/applications", tags=["applications"])


async def require_user(authorization: str | None = Header(None)):
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization")
    return user


@router.get("", response_model=ApplicationListResponse, summary="List applications")
async def list_applications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    entrance: int | None = Query(None, ge=1, le=4),
    room: str | None = Query(None, min_length=1, max_length=10),
    date_from: date | None = None,
    date_to: date | None = None,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_list(
            channel,
            user_id=user_id,
            roles=roles,
            page=page,
            size=size,
            status=status_filter,
            entrance=entrance,
            room=room,
            date_from=date_from.isoformat() if date_from else None,
            date_to=date_to.isoformat() if date_to else None,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    items = [proto_application_to_response(item) for item in resp.items]
    return ApplicationListResponse(
        items=items,
        total=resp.total,
        page=resp.page,
        size=resp.size,
        pages=resp.pages,
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, summary="Create application")
async def create_application(
    body: ApplicationCreateRequest,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_create(
            channel,
            user_id=user_id,
            roles=roles,
            leave_time=body.leave_time.isoformat(),
            return_time=body.return_time.isoformat(),
            reason=body.reason,
            contact_phone=body.contact_phone,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_application_to_response(resp.application)


@router.get("/{application_id}", response_model=ApplicationDetailResponse, summary="Get application by ID")
async def get_application(
    application_id: str,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_get(channel, user_id=user_id, roles=roles, application_id=application_id)
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_detail_to_response(resp.application)


@router.patch("/{application_id}", response_model=ApplicationResponse, summary="Approve or reject application")
async def decide_application(
    application_id: str,
    body: ApplicationDecideRequest,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_decide(
            channel,
            user_id=user_id,
            roles=roles,
            application_id=application_id,
            status=body.status,
            reject_reason=body.reject_reason,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_application_to_response(resp.application)


@router.post(
    "/{application_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
)
async def upload_document(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    data = await file.read()
    content_type = file.content_type or "application/octet-stream"
    filename = file.filename or "file"
    channel = get_channel()
    try:
        resp = await grpc_upload(
            channel,
            user_id=user_id,
            roles=roles,
            application_id=application_id,
            document_type=document_type,
            file_content=data,
            content_type=content_type,
            filename=filename,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_document_to_response(resp.document)


@router.get(
    "/{application_id}/documents/{document_id}/download",
    response_model=DocumentDownloadResponse,
    summary="Get presigned download URL for a document",
)
async def download_document(
    application_id: str,
    document_id: str,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_get_download_url(
            channel,
            user_id=user_id,
            roles=roles,
            application_id=application_id,
            document_id=document_id,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return DocumentDownloadResponse(url=resp.url)


@router.delete(
    "/{application_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document (owner or educator, application must be pending)",
)
async def delete_document(
    application_id: str,
    document_id: str,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        await grpc_delete_document(
            channel,
            user_id=user_id,
            roles=roles,
            application_id=application_id,
            document_id=document_id,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
