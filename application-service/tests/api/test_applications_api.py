"""API tests for applications list/detail: query params (entrance, room) and response fields (can_decide, user_name, room, entrance)."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.api.v1.applications.routers import router as applications_router
from src.dependencies import get_auth_client_dep, get_current_user, get_application_service
from src.grpc_clients.auth_client import AuthClientStub


def _make_mock_app(user_id=None):
    uid = user_id or uuid4()
    now = datetime.now(timezone.utc)
    obj = object.__new__(type("MockApp", (), {}))
    obj.id = uuid4()
    obj.user_id = uid
    obj.is_minor = False
    obj.leave_time = now
    obj.return_time = now
    obj.reason = "Test"
    obj.contact_phone = "+79001234567"
    obj.status = "pending"
    obj.decided_by = None
    obj.decided_at = None
    obj.reject_reason = None
    obj.created_at = now
    obj.updated_at = now
    obj.documents = []
    return obj


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(applications_router, prefix="/api/v1")
    return app


@pytest.fixture
def mock_user_id():
    return uuid4()


@pytest.fixture
def mock_app(mock_user_id):
    return _make_mock_app(mock_user_id)


@pytest.fixture
def mock_service(mock_app):
    class MockService:
        async def list_applications(self, *, user_id=None, entrance=None, room=None, status=None, date_from=None, date_to=None, page=1, size=20):
            return [mock_app], 1

        async def get_application(self, application_id, current_user_id, current_user_roles):
            return mock_app
    return MockService()


@pytest.fixture
def auth_stub():
    return AuthClientStub()


@pytest.fixture
async def client(app, mock_user_id, mock_service, auth_stub):
    async def override_get_current_user():
        return (mock_user_id, ["educator"])

    def override_get_application_service():
        return mock_service

    def override_get_auth_client():
        return auth_stub

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_application_service] = override_get_application_service
    app.dependency_overrides[get_auth_client_dep] = override_get_auth_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_applications_accepts_entrance_and_room(client, mock_app):
    r = await client.get(
        "/api/v1/applications",
        params={"entrance": 1, "room": "301", "page": 1, "size": 20},
        headers={"Authorization": "Bearer test-token"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert "user_name" in item
    assert "room" in item
    assert "entrance" in item
    assert item["user_name"] == "Иванов Иван Иванович"
    assert item["room"] == "301"
    assert item["entrance"] == 1


@pytest.mark.asyncio
async def test_get_application_returns_can_decide_and_enriched_fields(client, mock_app, auth_stub):
    r = await client.get(
        f"/api/v1/applications/{mock_app.id}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "can_decide" in data
    assert data["can_decide"] is True
    assert data.get("user_name") == "Иванов Иван Иванович"
    assert data.get("room") == "301"
    assert data.get("entrance") == 1
    assert "documents" in data
