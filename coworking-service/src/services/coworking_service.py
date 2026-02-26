from datetime import datetime
from uuid import UUID

import structlog

from src.constants.booking_status import (
    BOOKING_STATUS_ACTIVE,
    BOOKING_STATUS_CANCELLED,
    BOOKING_STATUS_COMPLETED,
    BOOKING_STATUS_CREATED,
)
from src.domain.exceptions import (
    BookingAccessDeniedError,
    BookingInvalidStatusTransitionError,
    BookingNotFoundError,
    CoworkingNotAvailableError,
    CoworkingNotFoundError,
    StudentAlreadyHasActiveBookingError,
)
from src.grpc_clients.auth_client import AuthClientProtocol
from src.repositories.booking_repository import BookingRepository
from src.repositories.coworking_repository import CoworkingRepository

logger = structlog.get_logger(__name__)

EDUCATOR_ROLES = ("educator", "educator_head", "admin")


class CoworkingService:
    def __init__(
        self,
        coworking_repository: CoworkingRepository,
        booking_repository: BookingRepository,
        auth_client: AuthClientProtocol,
    ) -> None:
        self._coworking_repo = coworking_repository
        self._booking_repo = booking_repository
        self._auth = auth_client

    async def list_coworkings(
        self,
        *,
        building: int | None = None,
        entrance: int | None = None,
        available: bool | None = None,
    ) -> list[object]:
        items = await self._coworking_repo.get_list(
            building=building,
            entrance=entrance,
            available=available,
        )
        return items

    async def get_coworking(self, coworking_id: UUID) -> object:
        coworking = await self._coworking_repo.get_by_id(coworking_id)
        if not coworking:
            raise CoworkingNotFoundError(str(coworking_id))
        return coworking

    async def create_booking(
        self,
        student_id: UUID,
        coworking_id: UUID,
        taken_from: datetime,
        returned_back: datetime,
    ) -> object:
        coworking = await self._coworking_repo.get_by_id(coworking_id)
        if not coworking:
            raise CoworkingNotFoundError(str(coworking_id))
        if not coworking.available:
            raise CoworkingNotAvailableError()

        has_active = await self._booking_repo.has_active_or_created_booking(student_id)
        if has_active:
            raise StudentAlreadyHasActiveBookingError()

        booking = await self._booking_repo.create(
            student_id=student_id,
            coworking_id=coworking_id,
            taken_from=taken_from,
            returned_back=returned_back,
        )

        logger.info(
            "booking_created",
            booking_id=str(booking.id),
            student_id=str(student_id),
            coworking_id=str(coworking_id),
        )
        return booking

    async def list_bookings(
        self,
        *,
        status: str | None = None,
        coworking_id: UUID | None = None,
        student_id: UUID | None = None,
        coworking_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[object], int]:
        items, total = await self._booking_repo.get_list(
            status=status,
            coworking_id=coworking_id,
            student_id=student_id,
            coworking_name=coworking_name,
            limit=limit,
            offset=offset,
        )
        return items, total

    async def get_my_bookings(
        self,
        *,
        student_id: UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[object], int]:
        items, total = await self._booking_repo.get_my_bookings(
            student_id=student_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        return items, total

    async def get_active_bookings(self) -> list[object]:
        return await self._booking_repo.get_active_bookings()

    async def get_booking_history(
        self,
        *,
        coworking_id: UUID | None = None,
        coworking_name: str | None = None,
        student_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[object], int]:
        items, total = await self._booking_repo.get_history(
            coworking_id=coworking_id,
            coworking_name=coworking_name,
            student_id=student_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return items, total

    async def get_booking(
        self,
        booking_id: UUID,
        current_user_id: UUID,
        current_user_roles: list[str],
    ) -> object:
        booking = await self._booking_repo.get_by_id_with_coworking(booking_id)
        if not booking:
            raise BookingNotFoundError(str(booking_id))

        is_owner = booking.student_id == current_user_id
        is_educator = any(r in current_user_roles for r in EDUCATOR_ROLES)
        if not is_owner and not is_educator:
            raise BookingAccessDeniedError()

        return booking

    async def confirm_booking(self, booking_id: UUID) -> object:
        booking = await self._booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(str(booking_id))
        if booking.status != BOOKING_STATUS_CREATED:
            raise BookingInvalidStatusTransitionError(booking.status, "confirm")

        await self._coworking_repo.update_availability(booking.coworking_id, False)

        updated = await self._booking_repo.update_status(booking_id, BOOKING_STATUS_ACTIVE)
        logger.info(
            "booking_confirmed",
            booking_id=str(booking_id),
        )
        return updated

    async def close_booking(self, booking_id: UUID) -> object:
        booking = await self._booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(str(booking_id))
        if booking.status != BOOKING_STATUS_ACTIVE:
            raise BookingInvalidStatusTransitionError(booking.status, "close")

        await self._coworking_repo.update_availability(booking.coworking_id, True)

        updated = await self._booking_repo.update_status(booking_id, BOOKING_STATUS_COMPLETED)
        logger.info(
            "booking_closed",
            booking_id=str(booking_id),
        )
        return updated

    async def cancel_booking(
        self,
        booking_id: UUID,
        current_user_id: UUID,
        current_user_roles: list[str],
    ) -> object:
        booking = await self._booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(str(booking_id))

        is_owner = booking.student_id == current_user_id
        is_educator = any(r in current_user_roles for r in EDUCATOR_ROLES)
        if not is_owner and not is_educator:
            raise BookingAccessDeniedError()

        if booking.status != BOOKING_STATUS_CREATED:
            raise BookingInvalidStatusTransitionError(booking.status, "cancel")

        updated = await self._booking_repo.update_status(booking_id, BOOKING_STATUS_CANCELLED)
        logger.info(
            "booking_cancelled",
            booking_id=str(booking_id),
            cancelled_by=str(current_user_id),
        )
        return updated
