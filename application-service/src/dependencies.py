from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.grpc_clients.auth_client import AuthClientProtocol, get_auth_client
from src.repositories.application_document_repository import ApplicationDocumentRepository
from src.repositories.application_repository import ApplicationRepository
from src.services.application_service import ApplicationService
from src.storage.minio_storage import MinioStorage


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_application_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ApplicationRepository:
    return ApplicationRepository(session)


def get_document_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ApplicationDocumentRepository:
    return ApplicationDocumentRepository(session)


def get_storage() -> MinioStorage:
    return MinioStorage()


def get_auth_client_dep() -> AuthClientProtocol:
    return get_auth_client()


def get_application_service(
    app_repo: ApplicationRepository = Depends(get_application_repository),
    doc_repo: ApplicationDocumentRepository = Depends(get_document_repository),
    storage: MinioStorage = Depends(get_storage),
    auth_client: AuthClientProtocol = Depends(get_auth_client_dep),
) -> ApplicationService:
    return ApplicationService(
        application_repository=app_repo,
        document_repository=doc_repo,
        storage=storage,
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
