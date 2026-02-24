from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.api.v1.patrols.schemas import (
    PatrolCreateRequest,
    PatrolUpdateRequest,
    PatrolEntryUpdateRequest,
    PatrolDetailResponse,
    PatrolListResponse,
    PatrolEntryResponse,
    PatrolResponse,
)
from src.dependencies import (
    get_patrol_service,
    get_current_user,
)
from src.services.patrol_service import PatrolService

router = APIRouter(prefix="/patrols", tags=["Patrols"])


def _to_patrol_response(model: object) -> PatrolResponse:
    return PatrolResponse.model_validate(model)


def _to_detail_response(model: object) -> PatrolDetailResponse:
    return PatrolDetailResponse.model_validate(model)


def _to_entry_response(model: object) -> PatrolEntryResponse:
    return PatrolEntryResponse.model_validate(model)


@router.get(
    "",
    response_model=PatrolListResponse,
    summary="Получить список всех обходов",
)
async def list_patrols(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    patrol_date: date | None = Query(None, alias="date"),
    building: str | None = Query(None, pattern="^(8|9)$"),
    entrance: int | None = Query(None, ge=1, le=4),
    status_filter: str | None = Query(None, alias="status", pattern="^(in_progress|completed)$"),
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    items, total = await service.list_patrols(
        patrol_date=patrol_date,
        building=building,
        entrance=entrance,
        status=status_filter,
        page=page,
        size=size,
    )
    pages = (total + size - 1) // size if total else 0
    return PatrolListResponse(
        items=[_to_patrol_response(m) for m in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "",
    response_model=PatrolDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый сеанс обхода",
)
async def create_patrol(
    body: PatrolCreateRequest,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    patrol = await service.create_patrol(
        patrol_date=body.date,
        building=body.building,
        entrance=body.entrance,
    )
    return _to_detail_response(patrol)


@router.get(
    "/{patrolId}",
    response_model=PatrolDetailResponse,
    summary="Получить состояние обхода",
)
async def get_patrol(
    patrolId: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    patrol = await service.get_patrol(patrol_id=patrolId)
    return _to_detail_response(patrol)


@router.patch(
    "/{patrolId}",
    response_model=PatrolDetailResponse,
    summary="Обновить состояние обхода",
)
async def update_patrol(
    patrolId: UUID,
    body: PatrolUpdateRequest,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    patrol = await service.complete_patrol(patrol_id=patrolId)
    return _to_detail_response(patrol)


@router.delete(
    "/{patrolId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сеанс обхода",
)
async def delete_patrol(
    patrolId: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    await service.delete_patrol(patrol_id=patrolId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{patrolId}/{patrolEntryId}",
    response_model=PatrolEntryResponse,
    summary="Получить состояние записи проверяемого студента",
)
async def get_patrol_entry(
    patrolId: UUID,
    patrolEntryId: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    entry = await service.get_patrol_entry(
        patrol_id=patrolId,
        patrol_entry_id=patrolEntryId,
    )
    return _to_entry_response(entry)


@router.patch(
    "/{patrolId}/{patrolEntryId}",
    response_model=PatrolEntryResponse,
    summary="Обновить состояние студента",
)
async def update_patrol_entry(
    patrolId: UUID,
    patrolEntryId: UUID,
    body: PatrolEntryUpdateRequest,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: PatrolService = Depends(get_patrol_service),
):
    entry = await service.update_patrol_entry(
        patrol_id=patrolId,
        patrol_entry_id=patrolEntryId,
        is_present=body.is_present,
        absence_reason=body.absence_reason,
    )
    return _to_entry_response(entry)
