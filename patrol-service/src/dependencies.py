from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.grpc_clients.auth_client import AuthClientProtocol, get_auth_client
from src.grpc_clients.application_client import ApplicationClientProtocol, get_application_client
from src.repositories.patrol_repository import PatrolRepository
from src.repositories.patrol_entry_repository import PatrolEntryRepository
from src.services.patrol_service import PatrolService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_patrol_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PatrolRepository:
    return PatrolRepository(session)


def get_patrol_entry_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PatrolEntryRepository:
    return PatrolEntryRepository(session)


def get_auth_client_dep() -> AuthClientProtocol:
    return get_auth_client()


def get_application_client_dep() -> ApplicationClientProtocol:
    return get_application_client()


def get_patrol_service(
    patrol_repo: PatrolRepository = Depends(get_patrol_repository),
    entry_repo: PatrolEntryRepository = Depends(get_patrol_entry_repository),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
    application_client: ApplicationClientProtocol = Depends(get_application_client_dep),
) -> PatrolService:
    return PatrolService(
        patrol_repository=patrol_repo,
        patrol_entry_repository=entry_repo,
        auth_client=auth_client,
        application_client=application_client,
    )


async def get_current_user(
    authorization: str | None = Header(None),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> tuple[UUID, list[str]]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )
    validation = await auth_client.validate_token(token)
    if not validation or not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return UUID(validation.user_id), validation.roles
