from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.patrol_entry import PatrolEntryModel


class PatrolEntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, patrol_entry_id: UUID) -> PatrolEntryModel | None:
        result = await self._session.execute(
            select(PatrolEntryModel).where(PatrolEntryModel.patrol_entry_id == patrol_entry_id)
        )
        return result.scalar_one_or_none()

    async def get_by_patrol_and_entry_id(
        self,
        patrol_id: UUID,
        patrol_entry_id: UUID,
    ) -> PatrolEntryModel | None:
        result = await self._session.execute(
            select(PatrolEntryModel).where(
                and_(
                    PatrolEntryModel.patrol_id == patrol_id,
                    PatrolEntryModel.patrol_entry_id == patrol_entry_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_patrol_id(self, patrol_id: UUID) -> list[PatrolEntryModel]:
        result = await self._session.execute(
            select(PatrolEntryModel).where(PatrolEntryModel.patrol_id == patrol_id)
        )
        return list(result.scalars().all())

    async def get_by_patrol_and_user(
        self,
        patrol_id: UUID,
        user_id: UUID,
    ) -> PatrolEntryModel | None:
        result = await self._session.execute(
            select(PatrolEntryModel).where(
                and_(
                    PatrolEntryModel.patrol_id == patrol_id,
                    PatrolEntryModel.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        patrol_id: UUID,
        user_id: UUID,
        room: str,
        is_present: bool | None = None,
        absence_reason: str | None = None,
    ) -> PatrolEntryModel:
        model = PatrolEntryModel(
            patrol_id=patrol_id,
            user_id=user_id,
            room=room,
            is_present=is_present,
            absence_reason=absence_reason,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def update(
        self,
        patrol_entry_id: UUID,
        is_present: bool | None = None,
        absence_reason: str | None = None,
        checked_at: datetime | None = None,
    ) -> PatrolEntryModel | None:
        model = await self.get_by_id(patrol_entry_id)
        if model is None:
            return None
        if is_present is not None:
            model.is_present = is_present
        if absence_reason is not None:
            model.absence_reason = absence_reason
        if checked_at is not None:
            model.checked_at = checked_at
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def delete(self, patrol_entry_id: UUID) -> bool:
        model = await self.get_by_id(patrol_entry_id)
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def create_batch(self, entries: list[dict]) -> list[PatrolEntryModel]:
        models = []
        for entry in entries:
            model = PatrolEntryModel(
                patrol_id=entry["patrol_id"],
                user_id=entry["user_id"],
                room=entry["room"],
                is_present=entry.get("is_present"),
                absence_reason=entry.get("absence_reason"),
            )
            self._session.add(model)
            models.append(model)
        await self._session.flush()
        for model in models:
            await self._session.refresh(model)
        return models
