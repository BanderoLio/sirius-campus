from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import DutyReport, DutySchedule


class DutyReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        page: int,
        size: int,
        schedule_id: Optional[UUID],
        status: Optional[str],
        room_id: Optional[UUID],
    ) -> tuple[list[DutyReport], int]:
        query = select(DutyReport).join(DutySchedule, DutySchedule.id == DutyReport.schedule_id)
        if room_id:
            query = query.where(DutySchedule.room_id == room_id)
        if schedule_id:
            query = query.where(DutyReport.schedule_id == schedule_id)
        if status:
            query = query.where(DutyReport.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        query = query.offset((page - 1) * size).limit(size)
        items = (await self.session.execute(query)).scalars().all()
        return items, total

    async def get_by_id(self, report_id: UUID, with_relations: bool = False) -> DutyReport | None:
        query = select(DutyReport).where(DutyReport.id == report_id)
        if with_relations:
            query = query.options(selectinload(DutyReport.images), selectinload(DutyReport.schedule))
        return (await self.session.execute(query)).scalar_one_or_none()

    async def add(self, report: DutyReport) -> DutyReport:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def save(self, report: DutyReport) -> DutyReport:
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def delete(self, report: DutyReport) -> None:
        await self.session.delete(report)
        await self.session.commit()
