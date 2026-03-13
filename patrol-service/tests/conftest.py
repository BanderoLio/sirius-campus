import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import get_session
from src.main import app
from src.models.base import Base
from src.models.patrol import PatrolModel
from src.models.patrol_entry import PatrolEntryModel


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_factory() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_patrol_data() -> dict:
    return {
        "date": str(date.today()),
        "building": "8",
        "entrance": 1,
    }


@pytest.fixture
def sample_patrol(db_session: AsyncSession) -> PatrolModel:
    patrol = PatrolModel(
        patrol_id=uuid4(),
        date=date.today(),
        building="8",
        entrance=1,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
    )
    db_session.add(patrol)
    db_session.commit()
    return patrol


@pytest.fixture
def sample_patrol_entry(db_session: AsyncSession, sample_patrol: PatrolModel) -> PatrolEntryModel:
    entry = PatrolEntryModel(
        patrol_entry_id=uuid4(),
        patrol_id=sample_patrol.patrol_id,
        user_id=uuid4(),
        room="301",
        is_present=None,
        absence_reason=None,
    )
    db_session.add(entry)
    db_session.commit()
    return entry
