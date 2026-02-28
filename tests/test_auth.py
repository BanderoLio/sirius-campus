"""
Tests for auth endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "auth-service"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_student_missing_fields(client):
    """Test student registration with missing fields."""
    response = await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": "test@example.com"
        }
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_students_pagination(client):
    """Test listing students with pagination."""
    response = await client.get("/api/v1/auth/students?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data


@pytest.mark.asyncio
async def test_list_educators_pagination(client):
    """Test listing educators with pagination."""
    response = await client.get("/api/v1/auth/educators?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
