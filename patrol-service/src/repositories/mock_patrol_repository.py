from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from src.models.patrol import PatrolModel
from src.models.patrol_entry import PatrolEntryModel


class MockPatrolRepository:
    def __init__(self) -> None:
        self._patrols: dict[UUID, PatrolModel] = {}

    async def get_by_id(self, patrol_id: UUID) -> PatrolModel | None:
        return self._patrols.get(patrol_id)

    async def get_by_id_with_entries(self, patrol_id: UUID) -> PatrolModel | None:
        patrol = self._patrols.get(patrol_id)
        if patrol:
            from src.repositories.mock_patrol_entry_repository import _mock_patrol_entry_repository
            patrol.entries = [e for e in _mock_patrol_entry_repository._entries.values() if e.patrol_id == patrol_id]
        return patrol

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
        filtered = list(self._patrols.values())
        
        if patrol_date is not None:
            filtered = [p for p in filtered if p.date == patrol_date]
        if building is not None:
            filtered = [p for p in filtered if p.building == building]
        if entrance is not None:
            filtered = [p for p in filtered if p.entrance == entrance]
        if status is not None:
            filtered = [p for p in filtered if p.status == status]
        
        filtered.sort(key=lambda p: p.created_at, reverse=True)
        
        total = len(filtered)
        start = (page - 1) * size
        end = start + size
        return filtered[start:end], total

    async def get_by_date_building_entrance(
        self,
        patrol_date: date,
        building: str,
        entrance: int,
    ) -> PatrolModel | None:
        for patrol in self._patrols.values():
            if patrol.date == patrol_date and patrol.building == building and patrol.entrance == entrance:
                return patrol
        return None

    async def create(
        self,
        patrol_date: date,
        building: str,
        entrance: int,
        started_at,
    ) -> PatrolModel:
        patrol_id = uuid4()
        model = PatrolModel(
            patrol_id=patrol_id,
            date=patrol_date,
            building=building,
            entrance=entrance,
            status="in_progress",
            started_at=started_at,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._patrols[patrol_id] = model
        model.entries = []
        return model

    async def update_status(
        self,
        patrol_id: UUID,
        status: str,
        submitted_at=None,
    ) -> PatrolModel | None:
        model = self._patrols.get(patrol_id)
        if model is None:
            return None
        model.status = status
        model.submitted_at = submitted_at
        model.updated_at = datetime.now(timezone.utc)
        return model

    async def delete(self, patrol_id: UUID) -> bool:
        if patrol_id in self._patrols:
            del self._patrols[patrol_id]
            return True
        return False


_mock_patrol_repository = MockPatrolRepository()


def get_mock_patrol_repository() -> MockPatrolRepository:
    return _mock_patrol_repository
