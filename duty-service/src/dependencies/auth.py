from typing import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.exceptions import ForbiddenException, UnauthorizedException
from src.grpc_clients.auth_client import AuthenticatedUser, get_auth_client

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("Authorization token required")
    auth_client = get_auth_client()
    return await auth_client.validate_token(credentials.credentials)


def require_roles(allowed_roles: set[str]) -> Callable:
    async def _dependency(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if not set(current_user.roles).intersection(allowed_roles):
            raise ForbiddenException("Insufficient permissions")
        return current_user

    return _dependency


require_educator_or_admin = require_roles({"educator", "educator_head", "admin", "student_head"})
