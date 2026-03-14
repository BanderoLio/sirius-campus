from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DutySchedule


class DutyScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        page: int,
        size: int,
        room_id: Optional[UUID],
        duty_date_from: Optional[date],
        duty_date_to: Optional[date],
        status: Optional[str],
    ) -> tuple[list[DutySchedule], int]:
        query = select(DutySchedule)
        if room_id:
            query = query.where(DutySchedule.room_id == room_id)
        if duty_date_from:
            query = query.where(DutySchedule.duty_date >= duty_date_from)
        if duty_date_to:
            query = query.where(DutySchedule.duty_date <= duty_date_to)
        if status:
            query = query.where(DutySchedule.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        query = query.offset((page - 1) * size).limit(size)
        items = (await self.session.execute(query)).scalars().all()
        return items, total

    async def get_by_id(self, schedule_id: UUID) -> DutySchedule | None:
        query = select(DutySchedule).where(DutySchedule.id == schedule_id)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def get_by_room_and_date(self, room_id: UUID, duty_date: date) -> DutySchedule | None:
        query = select(DutySchedule).where(
            DutySchedule.room_id == room_id,
            DutySchedule.duty_date == duty_date,
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def add(self, schedule: DutySchedule) -> DutySchedule:
        self.session.add(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule

    async def save(self, schedule: DutySchedule) -> DutySchedule:
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule

    async def delete(self, schedule: DutySchedule) -> None:
        await self.session.delete(schedule)
        await self.session.commit()
