"""Unit tests for ApplicationService.list_applications (entrance/room filters)."""
from datetime import date
from uuid import UUID, uuid4

import pytest

from src.services.application_service import ApplicationService


class _App:
    __slots__ = ("id", "user_id", "is_minor", "status", "leave_time", "return_time", "reason", "contact_phone", "decided_by", "decided_at", "reject_reason", "created_at", "updated_at")

    def __init__(self, id: UUID, user_id: UUID) -> None:
        self.id = id
        self.user_id = user_id
        self.is_minor = False
        self.status = "pending"
        self.leave_time = None
        self.return_time = None
        self.reason = ""
        self.contact_phone = ""
        self.decided_by = None
        self.decided_at = None
        self.reject_reason = None
        self.created_at = None
        self.updated_at = None


class _AppRepo:
    def __init__(self, items: list, total: int) -> None:
        self._items = items
        self._total = total
        self.last_get_list_kw: dict | None = None

    async def get_list(
        self,
        *,
        user_id: UUID | None = None,
        user_ids: list[UUID] | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list, int]:
        self.last_get_list_kw = {
            "user_id": user_id,
            "user_ids": user_ids,
            "status": status,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "size": size,
        }
        return self._items, self._total


class _DocRepo:
    pass


class _Storage:
    pass


class _Auth:
    def __init__(self, user_ids: list[str]) -> None:
        self._user_ids = user_ids
        self.get_user_ids_called: list[tuple[int | None, str | None]] = []

    async def get_user_ids(
        self,
        *,
        entrance: int | None = None,
        room: str | None = None,
    ) -> list[str]:
        self.get_user_ids_called.append((entrance, room))
        return self._user_ids


@pytest.mark.asyncio
async def test_list_applications_educator_with_entrance_room_calls_auth_and_passes_user_ids() -> None:
    user_uuid = uuid4()
    auth = _Auth(user_ids=[str(user_uuid)])
    app = _App(id=uuid4(), user_id=user_uuid)
    app_repo = _AppRepo(items=[app], total=1)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=_DocRepo(),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=auth,  # type: ignore[arg-type]
    )

    items, total = await service.list_applications(
        user_id=None,
        entrance=1,
        room="301",
        page=1,
        size=20,
    )

    assert total == 1
    assert len(items) == 1
    assert auth.get_user_ids_called == [(1, "301")]
    assert app_repo.last_get_list_kw is not None
    assert app_repo.last_get_list_kw["user_id"] is None
    assert app_repo.last_get_list_kw["user_ids"] == [user_uuid]
    assert app_repo.last_get_list_kw["status"] is None
    assert app_repo.last_get_list_kw["page"] == 1
    assert app_repo.last_get_list_kw["size"] == 20


@pytest.mark.asyncio
async def test_list_applications_student_ignores_entrance_room() -> None:
    user_id = uuid4()
    auth = _Auth(user_ids=[])
    app_repo = _AppRepo(items=[], total=0)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=_DocRepo(),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=auth,  # type: ignore[arg-type]
    )

    items, total = await service.list_applications(
        user_id=user_id,
        entrance=1,
        room="301",
        page=1,
        size=20,
    )

    assert total == 0
    assert auth.get_user_ids_called == []
    assert app_repo.last_get_list_kw["user_id"] == user_id
    assert app_repo.last_get_list_kw["user_ids"] is None


@pytest.mark.asyncio
async def test_list_applications_educator_empty_filter_returns_empty() -> None:
    auth = _Auth(user_ids=[])
    app_repo = _AppRepo(items=[], total=0)

    service = ApplicationService(
        application_repository=app_repo,  # type: ignore[arg-type]
        document_repository=_DocRepo(),  # type: ignore[arg-type]
        storage=_Storage(),  # type: ignore[arg-type]
        auth_client=auth,  # type: ignore[arg-type]
    )

    items, total = await service.list_applications(
        user_id=None,
        entrance=2,
        room="401",
        page=1,
        size=20,
    )

    assert total == 0
    assert auth.get_user_ids_called == [(2, "401")]
    assert app_repo.last_get_list_kw["user_ids"] == []
