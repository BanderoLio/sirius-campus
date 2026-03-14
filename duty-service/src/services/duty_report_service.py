from datetime import datetime
from typing import Optional
from uuid import UUID

from src.database.models import DutyReport, ReportStatusEnum
from src.exceptions import ForbiddenException, NotFoundException
from src.grpc_clients.auth_client import AuthenticatedUser
from src.repositories.duty_report_repository import DutyReportRepository
from src.repositories.duty_schedule_repository import DutyScheduleRepository


class DutyReportService:
    def __init__(
        self,
        report_repository: DutyReportRepository,
        schedule_repository: DutyScheduleRepository,
    ) -> None:
        self.report_repository = report_repository
        self.schedule_repository = schedule_repository

    async def list(
        self,
        current_user: AuthenticatedUser,
        page: int,
        size: int,
        schedule_id: Optional[UUID],
        status: Optional[str],
    ) -> tuple[list[DutyReport], int]:
        is_student = "student" in current_user.roles and not set(current_user.roles).intersection({"student_head", "educator", "educator_head", "admin"})
        room_id = current_user.room_id if is_student else None
        if is_student and room_id is None:
            raise ForbiddenException("Student room is not defined")
        return await self.report_repository.list(page, size, schedule_id, status, room_id)

    async def create(self, current_user: AuthenticatedUser, schedule_id: UUID) -> DutyReport:
        schedule = await self.schedule_repository.get_by_id(schedule_id)
        if schedule is None:
            raise NotFoundException("Schedule not found")

        is_student = "student" in current_user.roles and not set(current_user.roles).intersection({"student_head", "educator", "educator_head", "admin"})
        if is_student and current_user.room_id != schedule.room_id:
            raise ForbiddenException("No access to this schedule")

        report = DutyReport(
            schedule_id=schedule_id,
            user_id=current_user.user_id,
            status=ReportStatusEnum.submitted,
        )
        return await self.report_repository.add(report)

    async def get(self, current_user: AuthenticatedUser, report_id: UUID) -> DutyReport:
        report = await self.report_repository.get_by_id(report_id, with_relations=True)
        if report is None:
            raise NotFoundException("Report not found")

        is_student = "student" in current_user.roles and not set(current_user.roles).intersection({"student_head", "educator", "educator_head", "admin"})
        if is_student and current_user.room_id != report.schedule.room_id:
            raise ForbiddenException("No access to this report")

        return report

    async def update(self, report_id: UUID, schedule_id: UUID, status: ReportStatusEnum) -> DutyReport:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise NotFoundException("Report not found")
        report.schedule_id = schedule_id
        report.status = status
        return await self.report_repository.save(report)

    async def patch(
        self,
        current_user: AuthenticatedUser,
        report_id: UUID,
        status: ReportStatusEnum | None,
        reject_reason: str | None,
    ) -> DutyReport:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise NotFoundException("Report not found")

        if status is not None:
            report.status = status
            if status in {ReportStatusEnum.accepted, ReportStatusEnum.rejected}:
                report.reviewed_at = datetime.utcnow()
                report.reviewed_by = current_user.user_id
            if status == ReportStatusEnum.rejected and reject_reason:
                report.reject_reason = reject_reason

        return await self.report_repository.save(report)

    async def delete(self, report_id: UUID) -> None:
        report = await self.report_repository.get_by_id(report_id)
        if report is None:
            raise NotFoundException("Report not found")
        await self.report_repository.delete(report)
