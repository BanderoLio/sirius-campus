import asyncio
from uuid import UUID

from src.database.models import DutyReportImage
from src.exceptions import NotFoundException
from src.repositories.duty_image_repository import DutyImageRepository
from src.storage.minio_storage import MinioStorage


class DutyImageService:
    def __init__(self, repository: DutyImageRepository, storage: MinioStorage) -> None:
        self.repository = repository
        self.storage = storage

    async def create(
        self,
        report_id: UUID,
        category_id: UUID,
        filename: str,
        content_type: str,
        payload: bytes,
    ) -> DutyReportImage:
        photo_url = await asyncio.to_thread(
            self.storage.upload_report_image,
            report_id,
            category_id,
            filename,
            content_type,
            payload,
        )
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
        await asyncio.to_thread(self.storage.delete_object_by_url, image.photo_url)
        await self.repository.delete(image)
