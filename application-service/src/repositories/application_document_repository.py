from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.application_document import ApplicationDocumentModel


class ApplicationDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, document_id: UUID) -> ApplicationDocumentModel | None:
        result = await self._session.execute(
            select(ApplicationDocumentModel).where(ApplicationDocumentModel.id == document_id)
        )
        return result.scalar_one_or_none()

    async def get_by_application_id(self, application_id: UUID) -> list[ApplicationDocumentModel]:
        result = await self._session.execute(
            select(ApplicationDocumentModel).where(
                ApplicationDocumentModel.application_id == application_id
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        application_id: UUID,
        document_type: str,
        file_url: str,
        uploaded_by: UUID,
        document_id: UUID | None = None,
    ) -> ApplicationDocumentModel:
        kwargs: dict = {
            "application_id": application_id,
            "document_type": document_type,
            "file_url": file_url,
            "uploaded_by": uploaded_by,
        }
        if document_id is not None:
            kwargs["id"] = document_id
        model = ApplicationDocumentModel(**kwargs)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def count_voice_messages_for_application(self, application_id: UUID) -> int:
        from sqlalchemy import func

        result = await self._session.execute(
            select(func.count()).select_from(ApplicationDocumentModel).where(
                ApplicationDocumentModel.application_id == application_id,
                ApplicationDocumentModel.document_type == "voice_message",
            )
        )
        return result.scalar() or 0

    async def delete(self, document_id: UUID) -> bool:
        from sqlalchemy import delete

        result = await self._session.execute(
            delete(ApplicationDocumentModel).where(ApplicationDocumentModel.id == document_id)
        )
        return result.rowcount > 0
