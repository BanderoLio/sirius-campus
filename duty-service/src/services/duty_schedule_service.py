from datetime import date
from typing import Optional
from uuid import UUID

from src.database.models import DutySchedule, DutyStatusEnum
from src.exceptions import ConflictException, ForbiddenException, NotFoundException
from src.grpc_clients.auth_client import AuthenticatedUser
from src.repositories.duty_schedule_repository import DutyScheduleRepository


class DutyScheduleService:
    def __init__(self, repository: DutyScheduleRepository) -> None:
        self.repository = repository

    async def list(
        self,
        current_user: AuthenticatedUser,
        page: int,
        size: int,
        room_id: Optional[UUID],
        duty_date_from: Optional[date],
        duty_date_to: Optional[date],
        status: Optional[str],
    ) -> tuple[list[DutySchedule], int]:
        is_student = "student" in current_user.roles and not set(current_user.roles).intersection({"student_head", "educator", "educator_head", "admin"})
        effective_room_id = room_id
        if is_student:
            if current_user.room_id is None:
                raise ForbiddenException("Student room is not defined")
            effective_room_id = current_user.room_id

        return await self.repository.list(page, size, effective_room_id, duty_date_from, duty_date_to, status)

    async def create(self, current_user: AuthenticatedUser, room_id: UUID, duty_date: date) -> DutySchedule:
        duplicate = await self.repository.get_by_room_and_date(room_id, duty_date)
        if duplicate is not None:
            raise ConflictException("Duty schedule already exists for this room and date")

        schedule = DutySchedule(
            room_id=room_id,
            duty_date=duty_date,
            assigned_by=current_user.user_id,
            status=DutyStatusEnum.pending,
        )
        return await self.repository.add(schedule)

    async def get(self, current_user: AuthenticatedUser, schedule_id: UUID) -> DutySchedule:
        schedule = await self.repository.get_by_id(schedule_id)
        if schedule is None:
            raise NotFoundException("Schedule not found")

        is_student = "student" in current_user.roles and not set(current_user.roles).intersection({"student_head", "educator", "educator_head", "admin"})
        if is_student and current_user.room_id != schedule.room_id:
            raise ForbiddenException("No access to this schedule")

        return schedule

    async def update(
        self,
        schedule_id: UUID,
        room_id: UUID,
        duty_date: date,
        status: DutyStatusEnum,
    ) -> DutySchedule:
        schedule = await self.repository.get_by_id(schedule_id)
        if schedule is None:
            raise NotFoundException("Schedule not found")

        schedule.room_id = room_id
        schedule.duty_date = duty_date
        schedule.status = status
        return await self.repository.save(schedule)

    async def patch(self, schedule_id: UUID, status: DutyStatusEnum | None) -> DutySchedule:
        schedule = await self.repository.get_by_id(schedule_id)
        if schedule is None:
            raise NotFoundException("Schedule not found")

        if status is not None:
            schedule.status = status
        return await self.repository.save(schedule)

    async def delete(self, schedule_id: UUID) -> None:
        schedule = await self.repository.get_by_id(schedule_id)
        if schedule is None:
            raise NotFoundException("Schedule not found")
        await self.repository.delete(schedule)
