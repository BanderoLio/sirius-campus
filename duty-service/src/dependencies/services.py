from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.repositories.duty_schedule_repository import DutyScheduleRepository
from src.repositories.duty_report_repository import DutyReportRepository
from src.repositories.duty_image_repository import DutyImageRepository
from src.repositories.duty_category_repository import DutyCategoryRepository
from src.services.duty_schedule_service import DutyScheduleService
from src.services.duty_report_service import DutyReportService
from src.services.duty_image_service import DutyImageService
from src.services.duty_category_service import DutyCategoryService
from src.storage.minio_storage import get_minio_storage


def get_duty_schedule_service(session: AsyncSession = Depends(get_db)) -> DutyScheduleService:
    repository = DutyScheduleRepository(session)
    return DutyScheduleService(repository)


def get_duty_report_service(session: AsyncSession = Depends(get_db)) -> DutyReportService:
    report_repository = DutyReportRepository(session)
    schedule_repository = DutyScheduleRepository(session)
    return DutyReportService(report_repository=report_repository, schedule_repository=schedule_repository)


def get_duty_image_service(session: AsyncSession = Depends(get_db)) -> DutyImageService:
    repository = DutyImageRepository(session)
    storage = get_minio_storage()
    return DutyImageService(repository, storage)


def get_duty_category_service(session: AsyncSession = Depends(get_db)) -> DutyCategoryService:
    repository = DutyCategoryRepository(session)
    return DutyCategoryService(repository)
