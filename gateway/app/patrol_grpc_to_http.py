"""Convert gRPC proto messages to REST (Pydantic) and map gRPC status to HTTP."""
from datetime import date, datetime
from uuid import UUID

import grpc
from fastapi import HTTPException

from app.patrol_schemas import (
    PatrolCreateRequest,
    PatrolDetailResponse,
    PatrolEntryResponse,
    PatrolListResponse,
    PatrolResponse,
    PatrolUpdateRequest,
    PatrolEntryUpdateRequest,
)


def _parse_dt(s: str) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _parse_date(s: str) -> date | None:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _parse_uuid(s: str) -> UUID | None:
    if not s:
        return None
    try:
        return UUID(s)
    except (ValueError, TypeError):
        return None


def _parse_uuid_required(s: str) -> UUID:
    return _parse_uuid(s) or UUID("00000000-0000-0000-0000-000000000000")


def proto_patrol_entry_to_response(pb) -> PatrolEntryResponse:
    return PatrolEntryResponse(
        patrol_entry_id=_parse_uuid_required(pb.patrol_entry_id),
        patrol_id=_parse_uuid_required(pb.patrol_id),
        user_id=_parse_uuid_required(pb.user_id),
        user_name=pb.user_name or None,
        room=pb.room or "",
        is_present=pb.is_present if hasattr(pb, "is_present") else None,
        absence_reason=pb.absence_reason or None,
        checked_at=_parse_dt(pb.checked_at) if hasattr(pb, "checked_at") else None,
    )


def proto_patrol_to_response(pb) -> PatrolResponse:
    return PatrolResponse(
        patrol_id=_parse_uuid_required(pb.patrol_id),
        date=_parse_date(pb.date) or date.today(),
        building=pb.building or "",
        entrance=pb.entrance or "",
        patrol_by=_parse_uuid_required(pb.patrol_by) if hasattr(pb, "patrol_by") else UUID("00000000-0000-0000-0000-000000000000"),
        status=pb.status or "",
        started_at=_parse_dt(pb.started_at) or datetime.now(),
        submitted_at=_parse_dt(pb.submitted_at) if hasattr(pb, "submitted_at") else None,
    )


def proto_patrol_detail_to_response(pb) -> PatrolDetailResponse:
    base = proto_patrol_to_response(pb)
    entries = [proto_patrol_entry_to_response(e) for e in (pb.entries or [])]
    return PatrolDetailResponse(
        **base.model_dump(),
        entries=entries,
    )


def proto_patrol_list_to_response(pb) -> PatrolListResponse:
    items = [proto_patrol_to_response(item) for item in (pb.items or [])]
    return PatrolListResponse(
        items=items,
        total=pb.total,
        page=pb.page,
        size=pb.size,
        pages=pb.pages,
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
    if code == grpc.StatusCode.ALREADY_EXISTS:
        return HTTPException(status_code=409, detail=detail)
    if code == grpc.StatusCode.FAILED_PRECONDITION:
        return HTTPException(status_code=422, detail=detail)
    return HTTPException(status_code=500, detail=detail)
