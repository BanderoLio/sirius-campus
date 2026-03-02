import grpc
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.auth_stub import get_user_from_authorization
from app.patrol_grpc_client import (
    create_patrol as grpc_create,
    delete_patrol as grpc_delete,
    get_channel,
    get_patrol_details as grpc_get_details,
    get_patrol_entry as grpc_get_entry,
    list_patrols as grpc_list,
    update_patrol as grpc_update,
    update_patrol_entry as grpc_update_entry,
)
from app.patrol_grpc_to_http import (
    grpc_error_to_http,
    proto_patrol_detail_to_response,
    proto_patrol_entry_to_response,
    proto_patrol_list_to_response,
)
from app.patrol_schemas import (
    PatrolCreateRequest,
    PatrolDetailResponse,
    PatrolEntryResponse,
    PatrolEntryUpdateRequest,
    PatrolListResponse,
    PatrolResponse,
    PatrolUpdateRequest,
)

router = APIRouter(prefix="/patrols", tags=["patrols"])


async def require_user(authorization: str | None = Header(None)):
    user = get_user_from_authorization(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization")
    return user


@router.get("", response_model=PatrolListResponse, summary="List patrols")
async def list_patrols(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    date: str | None = Query(None),
    building: str | None = Query(None),
    entrance: int | None = Query(None, ge=1, le=4),
    status: str | None = Query(None),
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
            date=date,
            building=building,
            entrance=str(entrance) if entrance else None,
            status=status,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_patrol_list_to_response(resp)


@router.post("", response_model=PatrolDetailResponse, status_code=status.HTTP_201_CREATED, summary="Create patrol")
async def create_patrol(
    body: PatrolCreateRequest,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_create(
            channel,
            user_id=user_id,
            roles=roles,
            date=body.date.isoformat(),
            building=body.building,
            entrance=str(body.entrance),
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    # After creation, get full details
    try:
        details = await grpc_get_details(channel, user_id=user_id, roles=roles, patrol_id=resp.patrol_id)
    except grpc.RpcError:
        details = None
    if details:
        return proto_patrol_detail_to_response(details)
    # Fallback to basic response
    from app.patrol_grpc_to_http import proto_patrol_to_response
    return proto_patrol_to_response(resp)


@router.get("/{patrol_id}", response_model=PatrolDetailResponse, summary="Get patrol by ID")
async def get_patrol(
    patrol_id: str,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_get_details(channel, user_id=user_id, roles=roles, patrol_id=patrol_id)
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_patrol_detail_to_response(resp)


@router.patch("/{patrol_id}", response_model=PatrolDetailResponse, summary="Update patrol (complete)")
async def update_patrol(
    patrol_id: str,
    body: PatrolUpdateRequest,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        await grpc_update(channel, user_id=user_id, roles=roles, patrol_id=patrol_id, status=body.status)
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    # Get updated details
    try:
        details = await grpc_get_details(channel, user_id=user_id, roles=roles, patrol_id=patrol_id)
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_patrol_detail_to_response(details)


@router.delete("/{patrol_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete patrol")
async def delete_patrol(
    patrol_id: str,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        await grpc_delete(channel, user_id=user_id, roles=roles, patrol_id=patrol_id)
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)


@router.get("/{patrol_id}/{patrol_entry_id}", response_model=PatrolEntryResponse, summary="Get patrol entry")
async def get_patrol_entry(
    patrol_id: str,
    patrol_entry_id: str,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_get_entry(
            channel,
            user_id=user_id,
            roles=roles,
            patrol_id=patrol_id,
            patrol_entry_id=patrol_entry_id,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_patrol_entry_to_response(resp)


@router.patch("/{patrol_id}/{patrol_entry_id}", response_model=PatrolEntryResponse, summary="Update patrol entry")
async def update_patrol_entry(
    patrol_id: str,
    patrol_entry_id: str,
    body: PatrolEntryUpdateRequest,
    user: tuple[str, list[str]] = Depends(require_user),
):
    user_id, roles = user
    channel = get_channel()
    try:
        resp = await grpc_update_entry(
            channel,
            user_id=user_id,
            roles=roles,
            patrol_id=patrol_id,
            patrol_entry_id=patrol_entry_id,
            is_present=body.is_present,
            absence_reason=body.absence_reason,
        )
    except grpc.RpcError as e:
        raise grpc_error_to_http(e)
    return proto_patrol_entry_to_response(resp)
