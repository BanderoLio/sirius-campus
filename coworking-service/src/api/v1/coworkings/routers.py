from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.v1.coworkings.schemas import CoworkingResponse
from src.dependencies import get_coworking_service, get_current_user
from src.services.coworking_service import CoworkingService

router = APIRouter(prefix="/coworkings", tags=["Коворкинги"])


@router.get(
    "",
    response_model=list[CoworkingResponse],
    summary="Список коворкингов",
)
async def list_coworkings(
    building: int | None = Query(None, description="Фильтр по корпусу"),
    entrance: int | None = Query(None, description="Фильтр по подъезду"),
    available: bool | None = Query(None, description="Фильтр по доступности"),
    _current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
) -> list[CoworkingResponse]:
    items = await service.list_coworkings(
        building=building,
        entrance=entrance,
        available=available,
    )
    return [CoworkingResponse.model_validate(item) for item in items]


@router.get(
    "/{coworking_id}",
    response_model=CoworkingResponse,
    summary="Получить коворкинг по ID",
)
async def get_coworking(
    coworking_id: UUID,
    _current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
) -> CoworkingResponse:
    coworking = await service.get_coworking(coworking_id)
    return CoworkingResponse.model_validate(coworking)
