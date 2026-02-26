from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.constants.booking_status import BOOKING_STATUS_ACTIVE, BOOKING_STATUS_CREATED
from src.models.coworking import CoworkingModel
from src.models.coworking_booking import CoworkingBookingModel


class BookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, booking_id: UUID) -> CoworkingBookingModel | None:
        result = await self._session.execute(
            select(CoworkingBookingModel).where(CoworkingBookingModel.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_coworking(
        self, booking_id: UUID,
    ) -> CoworkingBookingModel | None:
        result = await self._session.execute(
            select(CoworkingBookingModel)
            .where(CoworkingBookingModel.id == booking_id)
            .options(selectinload(CoworkingBookingModel.coworking))
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        *,
        status: str | None = None,
        coworking_id: UUID | None = None,
        student_id: UUID | None = None,
        coworking_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[CoworkingBookingModel], int]:
        q = (
            select(CoworkingBookingModel)
            .options(selectinload(CoworkingBookingModel.coworking))
        )
        count_q = select(func.count()).select_from(CoworkingBookingModel)
        conditions = []

        if status is not None:
            conditions.append(CoworkingBookingModel.status == status)
        if coworking_id is not None:
            conditions.append(CoworkingBookingModel.coworking_id == coworking_id)
        if student_id is not None:
            conditions.append(CoworkingBookingModel.student_id == student_id)
        if coworking_name is not None:
            q = q.join(CoworkingModel)
            count_q = count_q.join(CoworkingModel)
            conditions.append(CoworkingModel.name.ilike(f"%{coworking_name}%"))

        if conditions:
            q = q.where(and_(*conditions))
            count_q = count_q.where(and_(*conditions))

        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0

        q = q.order_by(CoworkingBookingModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(q)
        rows = list(result.scalars().all())
        return rows, total

    async def get_my_bookings(
        self,
        *,
        student_id: UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[CoworkingBookingModel], int]:
        q = (
            select(CoworkingBookingModel)
            .options(selectinload(CoworkingBookingModel.coworking))
        )
        count_q = select(func.count()).select_from(CoworkingBookingModel)
        conditions = [CoworkingBookingModel.student_id == student_id]

        if status is not None:
            conditions.append(CoworkingBookingModel.status == status)

        q = q.where(and_(*conditions))
        count_q = count_q.where(and_(*conditions))

        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0

        q = q.order_by(CoworkingBookingModel.created_at.desc()).offset(offset).limit(limit)
        result = await self._session.execute(q)
        rows = list(result.scalars().all())
        return rows, total

    async def get_active_bookings(self) -> list[CoworkingBookingModel]:
        result = await self._session.execute(
            select(CoworkingBookingModel)
            .where(CoworkingBookingModel.status == BOOKING_STATUS_ACTIVE)
            .options(selectinload(CoworkingBookingModel.coworking))
            .order_by(CoworkingBookingModel.taken_from.asc())
        )
        return list(result.scalars().all())

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
    ) -> tuple[list[CoworkingBookingModel], int]:
        q = (
            select(CoworkingBookingModel)
            .options(selectinload(CoworkingBookingModel.coworking))
        )
        count_q = select(func.count()).select_from(CoworkingBookingModel)
        conditions: list = []
        need_join = False

        if coworking_id is not None:
            conditions.append(CoworkingBookingModel.coworking_id == coworking_id)
        if coworking_name is not None:
            need_join = True
            conditions.append(CoworkingModel.name.ilike(f"%{coworking_name}%"))
        if student_id is not None:
            conditions.append(CoworkingBookingModel.student_id == student_id)
        if date_from is not None:
            conditions.append(CoworkingBookingModel.taken_from >= date_from)
        if date_to is not None:
            conditions.append(CoworkingBookingModel.taken_from <= date_to)

        if need_join:
            q = q.join(CoworkingModel)
            count_q = count_q.join(CoworkingModel)

        if conditions:
            q = q.where(and_(*conditions))
            count_q = count_q.where(and_(*conditions))

        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0

        q = q.order_by(CoworkingBookingModel.taken_from.desc()).offset(offset).limit(limit)
        result = await self._session.execute(q)
        rows = list(result.scalars().all())
        return rows, total

    async def create(
        self,
        student_id: UUID,
        coworking_id: UUID,
        taken_from: datetime,
        returned_back: datetime,
    ) -> CoworkingBookingModel:
        model = CoworkingBookingModel(
            student_id=student_id,
            coworking_id=coworking_id,
            taken_from=taken_from,
            returned_back=returned_back,
            status=BOOKING_STATUS_CREATED,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["coworking"])
        return model

    async def update_status(
        self,
        booking_id: UUID,
        status: str,
    ) -> CoworkingBookingModel | None:
        model = await self.get_by_id(booking_id)
        if model is None:
            return None
        model.status = status
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def has_active_or_created_booking(self, student_id: UUID) -> bool:
        result = await self._session.execute(
            select(func.count())
            .select_from(CoworkingBookingModel)
            .where(
                and_(
                    CoworkingBookingModel.student_id == student_id,
                    or_(
                        CoworkingBookingModel.status == BOOKING_STATUS_CREATED,
                        CoworkingBookingModel.status == BOOKING_STATUS_ACTIVE,
                    ),
                )
            )
        )
        count = result.scalar() or 0
        return count > 0
