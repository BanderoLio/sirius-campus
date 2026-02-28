from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.patrol import PatrolModel


class PatrolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, patrol_id: UUID) -> PatrolModel | None:
        result = await self._session.execute(
            select(PatrolModel).where(PatrolModel.patrol_id == patrol_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_entries(self, patrol_id: UUID) -> PatrolModel | None:
        result = await self._session.execute(
            select(PatrolModel)
            .where(PatrolModel.patrol_id == patrol_id)
            .options(selectinload(PatrolModel.entries))
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        *,
        patrol_date: date | None = None,
        building: str | None = None,
        entrance: int | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[PatrolModel], int]:
        q = select(PatrolModel)
        count_q = select(func.count()).select_from(PatrolModel)
        conditions = []
        
        if patrol_date is not None:
            conditions.append(PatrolModel.date == patrol_date)
        if building is not None:
            conditions.append(PatrolModel.building == building)
        if entrance is not None:
            conditions.append(PatrolModel.entrance == entrance)
        if status is not None:
            conditions.append(PatrolModel.status == status)
        
        if conditions:
            q = q.where(and_(*conditions))
            count_q = count_q.where(and_(*conditions))
        
        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0
        
        q = q.order_by(PatrolModel.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await self._session.execute(q)
        rows = list(result.scalars().all())
        return rows, total

    async def get_by_date_building_entrance(
        self,
        patrol_date: date,
        building: str,
        entrance: int,
    ) -> PatrolModel | None:
        result = await self._session.execute(
            select(PatrolModel).where(
                and_(
                    PatrolModel.date == patrol_date,
                    PatrolModel.building == building,
                    PatrolModel.entrance == entrance,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        patrol_date: date,
        building: str,
        entrance: int,
        started_at,
    ) -> PatrolModel:
        model = PatrolModel(
            date=patrol_date,
            building=building,
            entrance=entrance,
            status="in_progress",
            started_at=started_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def update_status(
        self,
        patrol_id: UUID,
        status: str,
        submitted_at=None,
    ) -> PatrolModel | None:
        model = await self.get_by_id(patrol_id)
        if model is None:
            return None
        model.status = status
        if submitted_at is not None:
            model.submitted_at = submitted_at
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, patrol_id: UUID) -> bool:
        model = await self.get_by_id(patrol_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True
