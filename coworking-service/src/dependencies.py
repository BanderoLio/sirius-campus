from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.grpc_clients.auth_client import AuthClientProtocol, get_auth_client
from src.repositories.booking_repository import BookingRepository
from src.repositories.coworking_repository import CoworkingRepository
from src.services.coworking_service import CoworkingService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_coworking_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CoworkingRepository:
    return CoworkingRepository(session)


def get_booking_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BookingRepository:
    return BookingRepository(session)


def get_auth_client_dep() -> AuthClientProtocol:
    return get_auth_client()


def get_coworking_service(
    coworking_repo: CoworkingRepository = Depends(get_coworking_repository),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> CoworkingService:
    return CoworkingService(
        coworking_repository=coworking_repo,
        booking_repository=booking_repo,
        auth_client=auth_client,
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
