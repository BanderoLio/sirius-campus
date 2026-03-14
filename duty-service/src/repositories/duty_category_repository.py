from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DutyCategory


class DutyCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, page: int, size: int) -> tuple[list[DutyCategory], int]:
        query = select(DutyCategory)
        total = (await self.session.execute(select(func.count()).select_from(DutyCategory))).scalar() or 0
        query = query.offset((page - 1) * size).limit(size)
        items = (await self.session.execute(query)).scalars().all()
        return items, total
