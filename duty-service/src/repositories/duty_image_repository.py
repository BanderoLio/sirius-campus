from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import DutyReportImage


class DutyImageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id_for_report(self, image_id: UUID, report_id: UUID) -> DutyReportImage | None:
        query = select(DutyReportImage).where(
            DutyReportImage.id == image_id,
            DutyReportImage.report_id == report_id,
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def get_by_id(self, image_id: UUID) -> DutyReportImage | None:
        query = select(DutyReportImage).where(DutyReportImage.id == image_id)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def add(self, image: DutyReportImage) -> DutyReportImage:
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def save(self, image: DutyReportImage) -> DutyReportImage:
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def delete(self, image: DutyReportImage) -> None:
        await self.session.delete(image)
        await self.session.commit()
