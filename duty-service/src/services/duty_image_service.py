import asyncio
from uuid import UUID

from src.database import AsyncSessionLocal
from src.database.models import DutyReportImage
from src.exceptions import NotFoundException
from src.repositories.duty_image_repository import DutyImageRepository
from src.storage.minio_storage import MinioStorage, get_minio_storage


class DutyImageService:
    def __init__(self, repository: DutyImageRepository, storage: MinioStorage) -> None:
        self.repository = repository
        self.storage = storage

    async def create_pending(self, report_id: UUID, category_id: UUID) -> DutyReportImage:
        image = DutyReportImage(
            report_id=report_id,
            category_id=category_id,
            photo_url="uploading",
        )
        return await self.repository.add(image)

    async def delete(self, report_id: UUID, image_id: UUID) -> None:
        image = await self.repository.get_by_id_for_report(image_id=image_id, report_id=report_id)
        if image is None:
            raise NotFoundException("Image not found")
        if image.photo_url and image.photo_url != "uploading":
            await asyncio.to_thread(self.storage.delete_object_by_url, image.photo_url)
        await self.repository.delete(image)


async def upload_image_in_background(
    image_id: UUID,
    report_id: UUID,
    category_id: UUID,
    filename: str,
    content_type: str,
    payload: bytes,
) -> None:
    storage = get_minio_storage()
    photo_url = await asyncio.to_thread(
        storage.upload_report_image,
        report_id,
        category_id,
        filename,
        content_type,
        payload,
    )
    async with AsyncSessionLocal() as session:
        repository = DutyImageRepository(session)
        image = await repository.get_by_id(image_id)
        if image is None:
            await asyncio.to_thread(storage.delete_object_by_url, photo_url)
            return
        image.photo_url = photo_url
        await repository.save(image)
