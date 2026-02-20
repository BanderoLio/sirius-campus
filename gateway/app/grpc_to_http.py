"""Convert gRPC proto messages to REST (Pydantic) and map gRPC status to HTTP."""
from datetime import datetime
from uuid import UUID

import grpc
from fastapi import HTTPException

from app.schemas import (
    ApplicationDetailResponse,
    ApplicationListResponse,
    ApplicationResponse,
    DocumentDownloadResponse,
    DocumentResponse,
)


def _parse_dt(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _parse_uuid(s: str) -> UUID | None:
    if not s:
        return None
    try:
        return UUID(s)
    except (ValueError, TypeError):
        return None


def proto_application_to_response(pb) -> ApplicationResponse:
    return ApplicationResponse(
        id=_parse_uuid(pb.id) or UUID("00000000-0000-0000-0000-000000000000"),
        user_id=_parse_uuid(pb.user_id) or UUID("00000000-0000-0000-0000-000000000000"),
        is_minor=pb.is_minor,
        leave_time=_parse_dt(pb.leave_time) or datetime.now(),
        return_time=_parse_dt(pb.return_time) or datetime.now(),
        reason=pb.reason or "",
        contact_phone=pb.contact_phone or "",
        status=pb.status or "",
        decided_by=_parse_uuid(pb.decided_by) if pb.decided_by else None,
        decided_at=_parse_dt(pb.decided_at) if pb.decided_at else None,
        reject_reason=pb.reject_reason or None,
        created_at=_parse_dt(pb.created_at) or datetime.now(),
        updated_at=_parse_dt(pb.updated_at) or datetime.now(),
        user_name=pb.user_name or None,
        room=pb.room or None,
        entrance=pb.entrance if pb.entrance else None,
    )


def proto_document_to_response(pb) -> DocumentResponse:
    return DocumentResponse(
        id=_parse_uuid(pb.id) or UUID("00000000-0000-0000-0000-000000000000"),
        application_id=_parse_uuid(pb.application_id) or UUID("00000000-0000-0000-0000-000000000000"),
        document_type=pb.document_type or "",
        file_url=pb.file_url or "",
        uploaded_by=_parse_uuid(pb.uploaded_by) or UUID("00000000-0000-0000-0000-000000000000"),
        created_at=_parse_dt(pb.created_at) or datetime.now(),
    )


def proto_detail_to_response(detail_pb) -> ApplicationDetailResponse:
    if detail_pb is None or not hasattr(detail_pb, "base") or detail_pb.base is None:
        raise ValueError("GetApplicationResponse.application or application.base is missing")
    base = detail_pb.base
    app = proto_application_to_response(base)
    documents = [proto_document_to_response(d) for d in (detail_pb.documents or []) if d is not None]
    return ApplicationDetailResponse(
        **app.model_dump(),
        documents=documents,
        can_decide=detail_pb.can_decide,
    )


def grpc_error_to_http(e: grpc.RpcError) -> HTTPException:
    code = e.code()
    detail = e.details() or str(code)
    if code == grpc.StatusCode.UNAUTHENTICATED:
        return HTTPException(status_code=401, detail=detail)
    if code == grpc.StatusCode.PERMISSION_DENIED:
        return HTTPException(status_code=403, detail=detail)
    if code == grpc.StatusCode.NOT_FOUND:
        return HTTPException(status_code=404, detail=detail)
    if code == grpc.StatusCode.INVALID_ARGUMENT:
        return HTTPException(status_code=400, detail=detail)
    if code == grpc.StatusCode.FAILED_PRECONDITION:
        return HTTPException(status_code=409, detail=detail)
    return HTTPException(status_code=500, detail=detail)
