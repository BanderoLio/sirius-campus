"""In-memory mock repositories for running without a database."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.constants.booking_status import BOOKING_STATUS_ACTIVE, BOOKING_STATUS_CREATED


@dataclass
class MockCoworking:
    id: UUID
    name: str
    building: int
    entrance: int
    number: int
    available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    bookings: list = field(default_factory=list)


@dataclass
class MockBooking:
    id: UUID
    student_id: UUID
    coworking_id: UUID
    taken_from: datetime
    returned_back: datetime
    status: str = BOOKING_STATUS_CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    coworking: MockCoworking | None = None


_COWORKINGS: list[MockCoworking] = [
    MockCoworking(id=UUID("a0000000-0000-0000-0000-000000000001"), name="Магнолия", building=8, entrance=1, number=1301),
    MockCoworking(id=UUID("a0000000-0000-0000-0000-000000000002"), name="Кипарис", building=8, entrance=2, number=2042),
    MockCoworking(id=UUID("a0000000-0000-0000-0000-000000000003"), name="Олеандр", building=9, entrance=1, number=3071),
    MockCoworking(id=UUID("a0000000-0000-0000-0000-000000000004"), name="Платан", building=9, entrance=2, number=4052),
    MockCoworking(id=UUID("a0000000-0000-0000-0000-000000000005"), name="Лаванда", building=9, entrance=1, number=5301),
]

_BOOKINGS: list[MockBooking] = []

_CW_INDEX: dict[UUID, MockCoworking] = {c.id: c for c in _COWORKINGS}


class MockCoworkingRepository:

    async def get_by_id(self, coworking_id: UUID) -> MockCoworking | None:
        return _CW_INDEX.get(coworking_id)

    async def get_list(
        self,
        *,
        building: int | None = None,
        entrance: int | None = None,
        available: bool | None = None,
    ) -> list[MockCoworking]:
        result = list(_COWORKINGS)
        if building is not None:
            result = [c for c in result if c.building == building]
        if entrance is not None:
            result = [c for c in result if c.entrance == entrance]
        if available is not None:
            result = [c for c in result if c.available == available]
        result.sort(key=lambda c: (c.building, c.entrance, c.name))
        return result

    async def update_availability(self, coworking_id: UUID, available: bool) -> MockCoworking | None:
        cw = _CW_INDEX.get(coworking_id)
        if cw is None:
            return None
        cw.available = available
        cw.updated_at = datetime.now(timezone.utc)
        return cw


class MockBookingRepository:

    async def get_by_id(self, booking_id: UUID) -> MockBooking | None:
        return next((b for b in _BOOKINGS if b.id == booking_id), None)

    async def get_by_id_with_coworking(self, booking_id: UUID) -> MockBooking | None:
        b = await self.get_by_id(booking_id)
        if b:
            b.coworking = _CW_INDEX.get(b.coworking_id)
        return b

    async def get_list(
        self,
        *,
        status: str | None = None,
        coworking_id: UUID | None = None,
        student_id: UUID | None = None,
        coworking_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MockBooking], int]:
        result = list(_BOOKINGS)
        if status is not None:
            result = [b for b in result if b.status == status]
        if coworking_id is not None:
            result = [b for b in result if b.coworking_id == coworking_id]
        if student_id is not None:
            result = [b for b in result if b.student_id == student_id]
        if coworking_name is not None:
            lower = coworking_name.lower()
            result = [b for b in result if _CW_INDEX.get(b.coworking_id) and lower in _CW_INDEX[b.coworking_id].name.lower()]
        result.sort(key=lambda b: b.created_at, reverse=True)
        total = len(result)
        items = result[offset : offset + limit]
        for b in items:
            b.coworking = _CW_INDEX.get(b.coworking_id)
        return items, total

    async def get_my_bookings(
        self,
        *,
        student_id: UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MockBooking], int]:
        result = [b for b in _BOOKINGS if b.student_id == student_id]
        if status is not None:
            result = [b for b in result if b.status == status]
        result.sort(key=lambda b: b.created_at, reverse=True)
        total = len(result)
        items = result[offset : offset + limit]
        for b in items:
            b.coworking = _CW_INDEX.get(b.coworking_id)
        return items, total

    async def get_active_bookings(self) -> list[MockBooking]:
        result = [b for b in _BOOKINGS if b.status == BOOKING_STATUS_ACTIVE]
        result.sort(key=lambda b: b.taken_from)
        for b in result:
            b.coworking = _CW_INDEX.get(b.coworking_id)
        return result

    async def get_history(
        self,
        *,
        coworking_id: UUID | None = None,
        coworking_name: str | None = None,
        student_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MockBooking], int]:
        result = list(_BOOKINGS)
        if coworking_id is not None:
            result = [b for b in result if b.coworking_id == coworking_id]
        if coworking_name is not None:
            lower = coworking_name.lower()
            result = [b for b in result if _CW_INDEX.get(b.coworking_id) and lower in _CW_INDEX[b.coworking_id].name.lower()]
        if student_id is not None:
            result = [b for b in result if b.student_id == student_id]
        if date_from is not None:
            result = [b for b in result if b.taken_from >= date_from]
        if date_to is not None:
            result = [b for b in result if b.taken_from <= date_to]
        result.sort(key=lambda b: b.taken_from, reverse=True)
        total = len(result)
        items = result[offset : offset + limit]
        for b in items:
            b.coworking = _CW_INDEX.get(b.coworking_id)
        return items, total

    async def create(
        self,
        student_id: UUID,
        coworking_id: UUID,
        taken_from: datetime,
        returned_back: datetime,
    ) -> MockBooking:
        booking = MockBooking(
            id=uuid4(),
            student_id=student_id,
            coworking_id=coworking_id,
            taken_from=taken_from,
            returned_back=returned_back,
            status=BOOKING_STATUS_CREATED,
            coworking=_CW_INDEX.get(coworking_id),
        )
        _BOOKINGS.append(booking)
        return booking

    async def update_status(self, booking_id: UUID, status: str) -> MockBooking | None:
        b = await self.get_by_id(booking_id)
        if b is None:
            return None
        b.status = status
        b.updated_at = datetime.now(timezone.utc)
        return b

    async def has_active_or_created_booking(self, student_id: UUID) -> bool:
        return any(
            b.student_id == student_id and b.status in (BOOKING_STATUS_CREATED, BOOKING_STATUS_ACTIVE)
            for b in _BOOKINGS
        )
