from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from src.domain.exceptions import ForbiddenApplicationError, ApplicationNotFoundError
from src.services.application_service import ApplicationService


@dataclass
class _App:
    id: UUID
    user_id: UUID
    is_minor: bool = False


@dataclass
class _Doc:
    id: UUID
    application_id: UUID
    file_url: str


class _AppRepo:
    def __init__(self, app: _App | None) -> None:
        self._app = app

    async def get_by_id(self, application_id: UUID):
        if self._app and self._app.id == application_id:
            return self._app
        return None


class _DocRepo:
    def __init__(self, doc: _Doc | None) -> None:
        self._doc = doc

    async def get_by_id(self, document_id: UUID):
        if self._doc and self._doc.id == document_id:
            return self._doc
        return None


class _Storage:
    async def get_presigned_download_url(self, object_name: str, expiry_seconds: int = 3600) -> str:
        return f"https://example.com/{object_name}?exp={expiry_seconds}"


class _Auth:
    async def get_user_info(self, user_id: str):
        return None

    async def validate_token(self, token: str):
        return None

    async def get_user_ids(self, *, entrance: int | None = None, room: str | None = None):
        return []


@pytest.mark.asyncio
async def test_download_url_owner_ok() -> None:
    app_id = uuid4()
    doc_id = uuid4()
    user_id = uuid4()
    app = _App(id=app_id, user_id=user_id)
    doc = _Doc(id=doc_id, application_id=app_id, file_url="obj/key")

    service = ApplicationService(
        application_repository=_AppRepo(app),  # type: ignore[arg-type]
        document_repository=_DocRepo(doc),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    url = await service.get_document_download_url(
        application_id=app_id,
        document_id=doc_id,
        current_user_id=user_id,
        current_user_roles=["student"],
        expiry_seconds=123,
    )
    assert "https://example.com/obj/key" in url


@pytest.mark.asyncio
async def test_download_url_forbidden_for_non_owner_student() -> None:
    app_id = uuid4()
    doc_id = uuid4()
    owner_id = uuid4()
    other_id = uuid4()
    app = _App(id=app_id, user_id=owner_id)
    doc = _Doc(id=doc_id, application_id=app_id, file_url="obj/key")

    service = ApplicationService(
        application_repository=_AppRepo(app),  # type: ignore[arg-type]
        document_repository=_DocRepo(doc),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    with pytest.raises(ForbiddenApplicationError):
        await service.get_document_download_url(
            application_id=app_id,
            document_id=doc_id,
            current_user_id=other_id,
            current_user_roles=["student"],
        )


@pytest.mark.asyncio
async def test_download_url_educator_ok() -> None:
    app_id = uuid4()
    doc_id = uuid4()
    owner_id = uuid4()
    educator_id = uuid4()
    app = _App(id=app_id, user_id=owner_id)
    doc = _Doc(id=doc_id, application_id=app_id, file_url="obj/key")

    service = ApplicationService(
        application_repository=_AppRepo(app),  # type: ignore[arg-type]
        document_repository=_DocRepo(doc),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    url = await service.get_document_download_url(
        application_id=app_id,
        document_id=doc_id,
        current_user_id=educator_id,
        current_user_roles=["educator"],
    )
    assert url.startswith("https://example.com/")


@pytest.mark.asyncio
async def test_download_url_application_not_found() -> None:
    app_id = uuid4()
    doc_id = uuid4()
    user_id = uuid4()

    service = ApplicationService(
        application_repository=_AppRepo(None),  # type: ignore[arg-type]
        document_repository=_DocRepo(None),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    with pytest.raises(ApplicationNotFoundError):
        await service.get_document_download_url(
            application_id=app_id,
            document_id=doc_id,
            current_user_id=user_id,
            current_user_roles=["student"],
        )

