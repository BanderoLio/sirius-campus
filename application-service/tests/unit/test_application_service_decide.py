"""Unit tests for ApplicationService.decide_application and ensure_minor_voice_if_required."""
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.domain.exceptions import (
    ApplicationAlreadyDecidedError,
    ApplicationNotFoundError,
    MinorVoiceRequiredError,
)
from src.services.application_service import ApplicationService


class _App:
    __slots__ = ("id", "user_id", "is_minor", "status")

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        is_minor: bool = False,
        status: str = "pending",
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_minor = is_minor
        self.status = status


class _AppRepo:
    def __init__(self, app: _App | None) -> None:
        self._app = app
        self.update_status_called: list[tuple[UUID, str]] = []

    async def get_by_id(self, application_id: UUID) -> _App | None:
        if self._app and self._app.id == application_id:
            return self._app
        return None

    async def update_status(
        self,
        application_id: UUID,
        status: str,
        decided_by: UUID,
        decided_at: datetime,
        reject_reason: str | None = None,
    ) -> _App:
        self.update_status_called.append((application_id, status))
        return _App(
            id=application_id,
            user_id=self._app.user_id if self._app else uuid4(),
            is_minor=self._app.is_minor if self._app else False,
            status=status,
        )


class _DocRepo:
    def __init__(self, voice_count: int = 0) -> None:
        self._voice_count = voice_count

    async def count_voice_messages_for_application(self, application_id: UUID) -> int:
        return self._voice_count


class _Storage:
    pass


class _Auth:
    pass


@pytest.mark.asyncio
async def test_decide_minor_without_voice_raises() -> None:
    app_id = uuid4()
    user_id = uuid4()
    app = _App(id=app_id, user_id=user_id, is_minor=True, status="pending")
    app_repo = _AppRepo(app)
    doc_repo = _DocRepo(voice_count=0)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=doc_repo,  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    with pytest.raises(MinorVoiceRequiredError):
        await service.decide_application(
            application_id=app_id,
            status="approved",
            decided_by=user_id,
            decided_at=datetime.now(timezone.utc),
        )

    assert len(app_repo.update_status_called) == 0


@pytest.mark.asyncio
async def test_decide_minor_with_voice_ok() -> None:
    app_id = uuid4()
    user_id = uuid4()
    app = _App(id=app_id, user_id=user_id, is_minor=True, status="pending")
    app_repo = _AppRepo(app)
    doc_repo = _DocRepo(voice_count=1)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=doc_repo,  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    result = await service.decide_application(
        application_id=app_id,
        status="approved",
        decided_by=user_id,
        decided_at=datetime.now(timezone.utc),
    )

    assert result.status == "approved"
    assert app_repo.update_status_called == [(app_id, "approved")]


@pytest.mark.asyncio
async def test_decide_not_minor_no_voice_required() -> None:
    app_id = uuid4()
    user_id = uuid4()
    app = _App(id=app_id, user_id=user_id, is_minor=False, status="pending")
    app_repo = _AppRepo(app)
    doc_repo = _DocRepo(voice_count=0)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=doc_repo,  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    result = await service.decide_application(
        application_id=app_id,
        status="rejected",
        decided_by=user_id,
        decided_at=datetime.now(timezone.utc),
        reject_reason="No",
    )

    assert result.status == "rejected"
    assert app_repo.update_status_called == [(app_id, "rejected")]


@pytest.mark.asyncio
async def test_decide_application_not_found() -> None:
    app_id = uuid4()
    user_id = uuid4()
    app_repo = _AppRepo(None)
    doc_repo = _DocRepo(0)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=doc_repo,  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    with pytest.raises(ApplicationNotFoundError):
        await service.decide_application(
            application_id=app_id,
            status="approved",
            decided_by=user_id,
            decided_at=datetime.now(timezone.utc),
        )


@pytest.mark.asyncio
async def test_decide_already_decided_raises() -> None:
    app_id = uuid4()
    user_id = uuid4()
    app = _App(id=app_id, user_id=user_id, is_minor=False, status="approved")
    app_repo = _AppRepo(app)
    doc_repo = _DocRepo(0)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=doc_repo,  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=_Auth(),  # type: ignore[arg-type]
    )

    with pytest.raises(ApplicationAlreadyDecidedError):
        await service.decide_application(
            application_id=app_id,
            status="rejected",
            decided_by=user_id,
            decided_at=datetime.now(timezone.utc),
        )
