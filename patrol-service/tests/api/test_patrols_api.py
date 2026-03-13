from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.models.patrol import PatrolModel
from src.models.patrol_entry import PatrolEntryModel


class TestPatrolAPI:
    """Tests for patrol API endpoints."""

    def test_health_liveness(self, client: TestClient):
        """Test liveness endpoint."""
        response = client.get("/health/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_readiness(self, client: TestClient):
        """Test readiness endpoint."""
        response = client.get("/health/readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    def test_list_patrols_empty(self, client: TestClient):
        """Test listing patrols when empty."""
        response = client.get(
            "/api/v1/patrols",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_create_patrol_unauthorized(self, client: TestClient):
        """Test creating patrol without authorization."""
        response = client.post(
            "/api/v1/patrols",
            json={
                "date": str(date.today()),
                "building": "8",
                "entrance": 1,
            },
        )
        assert response.status_code == 401

    def test_create_patrol_invalid_building(self, client: TestClient):
        """Test creating patrol with invalid building."""
        response = client.post(
            "/api/v1/patrols",
            json={
                "date": str(date.today()),
                "building": "7",
                "entrance": 1,
            },
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 422

    def test_create_patrol_invalid_entrance(self, client: TestClient):
        """Test creating patrol with invalid entrance."""
        response = client.post(
            "/api/v1/patrols",
            json={
                "date": str(date.today()),
                "building": "8",
                "entrance": 5,
            },
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 422

    def test_get_patrol_not_found(self, client: TestClient):
        """Test getting non-existent patrol."""
        patrol_id = uuid4()
        response = client.get(
            f"/api/v1/patrols/{patrol_id}",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "PATROL_NOT_FOUND"

    def test_delete_patrol_not_found(self, client: TestClient):
        """Test deleting non-existent patrol."""
        patrol_id = uuid4()
        response = client.delete(
            f"/api/v1/patrols/{patrol_id}",
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 404

    def test_update_patrol_entry_not_found(self, client: TestClient):
        """Test updating non-existent patrol entry."""
        patrol_id = uuid4()
        entry_id = uuid4()
        response = client.patch(
            f"/api/v1/patrols/{patrol_id}/{entry_id}",
            json={"is_present": True},
            headers={"Authorization": "Bearer test-token"},
        )
        assert response.status_code == 404
