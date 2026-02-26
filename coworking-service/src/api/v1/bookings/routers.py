from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.v1.bookings.schemas import (
    BookingCreateRequest,
    BookingDetailResponse,
    BookingListResponse,
    BookingResponse,
    StudentShort,
)
from src.api.v1.coworkings.schemas import CoworkingResponse
from src.dependencies import get_coworking_service, get_current_user
from src.domain.exceptions import BookingAccessDeniedError
from src.grpc_clients.auth_client import AuthClientProtocol
from src.dependencies import get_auth_client_dep
from src.services.coworking_service import CoworkingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

EDUCATOR_ROLES = ("educator", "educator_head", "admin")


async def _enrich_booking_detail(
    model: object,
    auth_client: AuthClientProtocol,
) -> BookingDetailResponse:
    booking = BookingDetailResponse.model_validate(model)
    user_info = await auth_client.get_user_info(str(booking.student_id))
    if user_info:
        booking.student = StudentShort(
            user_id=user_info.user_id,
            last_name=user_info.last_name,
            first_name=user_info.first_name,
            patronymic=user_info.patronymic,
            building=user_info.building,
            entrance=user_info.entrance,
            room=user_info.room,
        )
    coworking_attr = getattr(model, "coworking", None)
    if coworking_attr is not None:
        booking.coworking = CoworkingResponse.model_validate(coworking_attr)
    return booking


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бронирование",
)
async def create_booking(
    body: BookingCreateRequest,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
) -> BookingResponse:
    user_id, roles = current_user
    if any(r in roles for r in EDUCATOR_ROLES):
        raise BookingAccessDeniedError()
    booking = await service.create_booking(
        student_id=user_id,
        coworking_id=body.coworking_id,
        taken_from=body.taken_from,
        returned_back=body.returned_back,
    )
    return BookingResponse.model_validate(booking)


@router.get(
    "",
    response_model=BookingListResponse,
    summary="Список бронирований",
)
async def list_bookings(
    status_filter: str | None = Query(None, alias="status", description="Фильтр по статусу"),
    coworking_id: UUID | None = Query(None, description="Фильтр по ID коворкинга"),
    student_id: UUID | None = Query(None, description="Фильтр по ID студента"),
    coworking_name: str | None = Query(None, description="Фильтр по названию коворкинга"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> BookingListResponse:
    _, roles = current_user
    is_educator = any(r in roles for r in EDUCATOR_ROLES)
    if not is_educator:
        raise BookingAccessDeniedError()

    items, total = await service.list_bookings(
        status=status_filter,
        coworking_id=coworking_id,
        student_id=student_id,
        coworking_name=coworking_name,
        limit=limit,
        offset=offset,
    )
    enriched = [await _enrich_booking_detail(item, auth_client) for item in items]
    return BookingListResponse(items=enriched, total=total, limit=limit, offset=offset)


@router.get(
    "/my",
    response_model=BookingListResponse,
    summary="Мои бронирования",
)
async def get_my_bookings(
    status_filter: str | None = Query(None, alias="status", description="Фильтр по статусу"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> BookingListResponse:
    user_id, _ = current_user
    items, total = await service.get_my_bookings(
        student_id=user_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    enriched = [await _enrich_booking_detail(item, auth_client) for item in items]
    return BookingListResponse(items=enriched, total=total, limit=limit, offset=offset)


@router.get(
    "/active",
    response_model=list[BookingDetailResponse],
    summary="Активные бронирования (дашборд)",
)
async def get_active_bookings(
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> list[BookingDetailResponse]:
    _, roles = current_user
    is_educator = any(r in roles for r in EDUCATOR_ROLES)
    if not is_educator:
        raise BookingAccessDeniedError()

    items = await service.get_active_bookings()
    return [await _enrich_booking_detail(item, auth_client) for item in items]


@router.get(
    "/history",
    response_model=BookingListResponse,
    summary="История использования коворкингов",
)
async def get_booking_history(
    coworking_id: UUID | None = Query(None, description="Фильтр по ID коворкинга"),
    coworking_name: str | None = Query(None, description="Фильтр по названию коворкинга"),
    student_id: UUID | None = Query(None, description="Фильтр по ID студента"),
    date_from: datetime | None = Query(None, description="Начало периода"),
    date_to: datetime | None = Query(None, description="Конец периода"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> BookingListResponse:
    _, roles = current_user
    is_educator = any(r in roles for r in EDUCATOR_ROLES)
    if not is_educator:
        raise BookingAccessDeniedError()

    items, total = await service.get_booking_history(
        coworking_id=coworking_id,
        coworking_name=coworking_name,
        student_id=student_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    enriched = [await _enrich_booking_detail(item, auth_client) for item in items]
    return BookingListResponse(items=enriched, total=total, limit=limit, offset=offset)


@router.get(
    "/{booking_id}",
    response_model=BookingDetailResponse,
    summary="Получить бронирование по ID",
)
async def get_booking(
    booking_id: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> BookingDetailResponse:
    user_id, roles = current_user
    booking = await service.get_booking(
        booking_id=booking_id,
        current_user_id=user_id,
        current_user_roles=roles,
    )
    return await _enrich_booking_detail(booking, auth_client)


@router.patch(
    "/{booking_id}/confirm",
    response_model=BookingResponse,
    summary="Подтвердить бронирование (выдать ключ)",
)
async def confirm_booking(
    booking_id: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
) -> BookingResponse:
    _, roles = current_user
    is_educator = any(r in roles for r in EDUCATOR_ROLES)
    if not is_educator:
        raise BookingAccessDeniedError()

    updated = await service.confirm_booking(booking_id)
    return BookingResponse.model_validate(updated)


@router.patch(
    "/{booking_id}/close",
    response_model=BookingResponse,
    summary="Закрыть бронирование (принять ключ)",
)
async def close_booking(
    booking_id: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
) -> BookingResponse:
    _, roles = current_user
    is_educator = any(r in roles for r in EDUCATOR_ROLES)
    if not is_educator:
        raise BookingAccessDeniedError()

    updated = await service.close_booking(booking_id)
    return BookingResponse.model_validate(updated)


@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    summary="Отменить бронирование",
)
async def cancel_booking(
    booking_id: UUID,
    current_user: tuple[UUID, list[str]] = Depends(get_current_user),
    service: CoworkingService = Depends(get_coworking_service),
) -> BookingResponse:
    user_id, roles = current_user
    updated = await service.cancel_booking(
        booking_id=booking_id,
        current_user_id=user_id,
        current_user_roles=roles,
    )
    return BookingResponse.model_validate(updated)
