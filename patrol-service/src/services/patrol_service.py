from datetime import date, datetime, timezone
from uuid import UUID

from src.domain.exceptions import (
    PatrolAlreadyCompletedError,
    PatrolAlreadyExistsError,
    PatrolEntryNotFoundError,
    PatrolNotFoundError,
    PatrolNotInProgressError,
    ValidationError,
)
from src.grpc_clients.auth_client import AuthClientProtocol
from src.grpc_clients.application_client import ApplicationClientProtocol
from src.repositories.patrol_repository import PatrolRepository
from src.repositories.patrol_entry_repository import PatrolEntryRepository


class PatrolService:
    def __init__(
        self,
        patrol_repository: PatrolRepository,
        patrol_entry_repository: PatrolEntryRepository,
        auth_client: AuthClientProtocol,
        application_client: ApplicationClientProtocol,
    ) -> None:
        self._patrol_repo = patrol_repository
        self._entry_repo = patrol_entry_repository
        self._auth = auth_client
        self._application = application_client

    async def create_patrol(
        self,
        patrol_date: date,
        building: str,
        entrance: int,
    ) -> object:
        # Validate building
        if building not in ("8", "9"):
            raise ValidationError("Корпус должен быть 8 или 9")
        
        # Validate entrance
        if entrance < 1 or entrance > 4:
            raise ValidationError("Подъезд должен быть от 1 до 4")

        # Check if patrol already exists
        existing = await self._patrol_repo.get_by_date_building_entrance(
            patrol_date=patrol_date,
            building=building,
            entrance=entrance,
        )
        if existing:
            raise PatrolAlreadyExistsError(
                building=building,
                entrance=entrance,
                date=str(patrol_date),
            )

        # Create patrol
        started_at = datetime.now(timezone.utc)
        patrol = await self._patrol_repo.create(
            patrol_date=patrol_date,
            building=building,
            entrance=entrance,
            started_at=started_at,
        )

        # Get minor students from auth-service
        minor_students = await self._auth.get_minor_students_by_entrance(
            building=building,
            entrance=entrance,
        )

        # Get approved leaves from application-service
        approved_leaves = await self._application.get_approved_leaves(
            date=str(patrol_date),
            building=building,
            entrance=entrance,
        )

        # Create a map of user_id -> leave record for quick lookup
        leave_map = {leave.user_id: leave for leave in approved_leaves}

        # Create entries for each minor student
        entries_to_create = []
        for student in minor_students:
            entry_data = {
                "patrol_id": patrol.patrol_id,
                "user_id": UUID(student.user_id),
                "room": student.room,
            }
            
            # Check if student has approved leave
            if student.user_id in leave_map:
                leave = leave_map[student.user_id]
                entry_data["is_present"] = False
                entry_data["absence_reason"] = f"Заявление на выход: {leave.reason}"
            
            entries_to_create.append(entry_data)

        if entries_to_create:
            await self._entry_repo.create_batch(entries_to_create)

        # Return patrol with entries
        return await self._patrol_repo.get_by_id_with_entries(patrol.patrol_id)

    async def get_patrol(self, patrol_id: UUID) -> object:
        patrol = await self._patrol_repo.get_by_id_with_entries(patrol_id)
        if not patrol:
            raise PatrolNotFoundError(str(patrol_id))
        return patrol

    async def list_patrols(
        self,
        *,
        patrol_date: date | None = None,
        building: str | None = None,
        entrance: int | None = None,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[object], int]:
        return await self._patrol_repo.get_list(
            patrol_date=patrol_date,
            building=building,
            entrance=entrance,
            status=status,
            page=page,
            size=size,
        )

    async def complete_patrol(self, patrol_id: UUID) -> object:
        patrol = await self._patrol_repo.get_by_id(patrol_id)
        if not patrol:
            raise PatrolNotFoundError(str(patrol_id))
        
        if patrol.status == "completed":
            raise PatrolAlreadyCompletedError()

        submitted_at = datetime.now(timezone.utc)
        updated = await self._patrol_repo.update_status(
            patrol_id=patrol_id,
            status="completed",
            submitted_at=submitted_at,
        )
        
        return await self._patrol_repo.get_by_id_with_entries(patrol_id)

    async def delete_patrol(self, patrol_id: UUID) -> bool:
        patrol = await self._patrol_repo.get_by_id(patrol_id)
        if not patrol:
            raise PatrolNotFoundError(str(patrol_id))
        return await self._patrol_repo.delete(patrol_id)

    async def get_patrol_entry(
        self,
        patrol_id: UUID,
        patrol_entry_id: UUID,
    ) -> object:
        entry = await self._entry_repo.get_by_patrol_and_entry_id(
            patrol_id=patrol_id,
            patrol_entry_id=patrol_entry_id,
        )
        if not entry:
            raise PatrolEntryNotFoundError(str(patrol_entry_id))
        return entry

    async def update_patrol_entry(
        self,
        patrol_id: UUID,
        patrol_entry_id: UUID,
        is_present: bool | None = None,
        absence_reason: str | None = None,
    ) -> object:
        # Check patrol exists and is in progress
        patrol = await self._patrol_repo.get_by_id(patrol_id)
        if not patrol:
            raise PatrolNotFoundError(str(patrol_id))
        
        if patrol.status != "in_progress":
            raise PatrolNotInProgressError()

        # Check entry exists
        entry = await self._entry_repo.get_by_patrol_and_entry_id(
            patrol_id=patrol_id,
            patrol_entry_id=patrol_entry_id,
        )
        if not entry:
            raise PatrolEntryNotFoundError(str(patrol_entry_id))

        # Update entry
        checked_at = datetime.now(timezone.utc)
        updated = await self._entry_repo.update(
            patrol_entry_id=patrol_entry_id,
            is_present=is_present,
            absence_reason=absence_reason,
            checked_at=checked_at,
        )
        
        return updated
