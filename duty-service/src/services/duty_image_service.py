from uuid import UUID

from src.database.models import DutyReportImage
from src.exceptions import NotFoundException
from src.repositories.duty_image_repository import DutyImageRepository


class DutyImageService:
    def __init__(self, repository: DutyImageRepository) -> None:
        self.repository = repository

    async def create(self, report_id: UUID, category_id: UUID, photo_url: str) -> DutyReportImage:
        image = DutyReportImage(
            report_id=report_id,
            category_id=category_id,
            photo_url=photo_url,
        )
        return await self.repository.add(image)

    async def delete(self, report_id: UUID, image_id: UUID) -> None:
        image = await self.repository.get_by_id_for_report(image_id=image_id, report_id=report_id)
        if image is None:
            raise NotFoundException("Image not found")
        await self.repository.delete(image)
