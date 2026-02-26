from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.coworking import CoworkingModel


class CoworkingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, coworking_id: UUID) -> CoworkingModel | None:
        result = await self._session.execute(
            select(CoworkingModel).where(CoworkingModel.id == coworking_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        *,
        building: int | None = None,
        entrance: int | None = None,
        available: bool | None = None,
    ) -> list[CoworkingModel]:
        q = select(CoworkingModel)
        conditions = []

        if building is not None:
            conditions.append(CoworkingModel.building == building)
        if entrance is not None:
            conditions.append(CoworkingModel.entrance == entrance)
        if available is not None:
            conditions.append(CoworkingModel.available == available)

        if conditions:
            q = q.where(and_(*conditions))

        q = q.order_by(CoworkingModel.building, CoworkingModel.entrance, CoworkingModel.name)
        result = await self._session.execute(q)
        return list(result.scalars().all())

    async def update_availability(
        self,
        coworking_id: UUID,
        available: bool,
    ) -> CoworkingModel | None:
        model = await self.get_by_id(coworking_id)
        if model is None:
            return None
        model.available = available
        await self._session.flush()
        await self._session.refresh(model)
        return model
