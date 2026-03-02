from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.models.patrol_entry import PatrolEntryModel


class MockPatrolEntryRepository:
    def __init__(self) -> None:
        self._entries: dict[UUID, PatrolEntryModel] = {}

    async def get_by_id(self, patrol_entry_id: UUID) -> PatrolEntryModel | None:
        return self._entries.get(patrol_entry_id)

    async def get_by_patrol_and_entry_id(
        self,
        patrol_id: UUID,
        patrol_entry_id: UUID,
    ) -> PatrolEntryModel | None:
        entry = self._entries.get(patrol_entry_id)
        if entry and entry.patrol_id == patrol_id:
            return entry
        return None

    async def get_by_patrol_id(self, patrol_id: UUID) -> list[PatrolEntryModel]:
        return [e for e in self._entries.values() if e.patrol_id == patrol_id]

    async def get_by_patrol_and_user(
        self,
        patrol_id: UUID,
        user_id: UUID,
    ) -> PatrolEntryModel | None:
        for entry in self._entries.values():
            if entry.patrol_id == patrol_id and entry.user_id == user_id:
                return entry
        return None

    async def create(
        self,
        patrol_id: UUID,
        user_id: UUID,
        room: str,
        is_present: bool | None = None,
        absence_reason: str | None = None,
    ) -> PatrolEntryModel:
        patrol_entry_id = uuid4()
        model = PatrolEntryModel(
            patrol_entry_id=patrol_entry_id,
            patrol_id=patrol_id,
            user_id=user_id,
            room=room,
            is_present=is_present,
            absence_reason=absence_reason,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._entries[patrol_entry_id] = model
        return model

    async def update(
        self,
        patrol_entry_id: UUID,
        is_present: bool | None = None,
        absence_reason: str | None = None,
        checked_at: datetime | None = None,
    ) -> PatrolEntryModel | None:
        model = self._entries.get(patrol_entry_id)
        if model is None:
            return None
        if is_present is not None:
            model.is_present = is_present
        if absence_reason is not None:
            model.absence_reason = absence_reason
        if checked_at is not None:
            model.checked_at = checked_at
        model.updated_at = datetime.now(timezone.utc)
        return model

    async def delete(self, patrol_entry_id: UUID) -> bool:
        if patrol_entry_id in self._entries:
            del self._entries[patrol_entry_id]
            return True
        return False

    async def create_batch(self, entries: list[dict]) -> list[PatrolEntryModel]:
        models = []
        for entry in entries:
            model = await self.create(
                patrol_id=entry["patrol_id"],
                user_id=entry["user_id"],
                room=entry["room"],
                is_present=entry.get("is_present"),
                absence_reason=entry.get("absence_reason"),
            )
            models.append(model)
        return models


_mock_patrol_entry_repository = MockPatrolEntryRepository()


def get_mock_patrol_entry_repository() -> MockPatrolEntryRepository:
    return _mock_patrol_entry_repository
