from dataclasses import dataclass
from typing import Protocol


@dataclass
class TokenValidation:
    valid: bool
    user_id: str
    roles: list[str]
    building: int
    entrance: int
    floor: int
    room: str
    is_minor: bool


@dataclass
class UserInfo:
    user_id: str
    last_name: str
    first_name: str
    patronymic: str
    building: int
    entrance: int
    floor: int
    room: str
    roles: list[str]
    phone: str
    email: str
    is_minor: bool


class AuthClientProtocol(Protocol):
    async def validate_token(self, token: str) -> TokenValidation | None: ...

    async def get_user_info(self, user_id: str) -> UserInfo | None: ...

    async def check_user_role(self, user_id: str, role: str) -> bool: ...


class AuthClientStub:
    """Stub for development when auth-service is not available."""

    async def validate_token(self, token: str) -> TokenValidation | None:
        if not token or token == "Bearer":
            return None
        token_clean = token.replace("Bearer ", "").strip()
        if not token_clean:
            return None
        return TokenValidation(
            valid=True,
            user_id="00000000-0000-0000-0000-000000000001",
            roles=["student"],
            building=8,
            entrance=1,
            floor=3,
            room="5142",
            is_minor=False,
        )

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        return UserInfo(
            user_id=user_id,
            last_name="Тарасенко",
            first_name="Алиса",
            patronymic="Дмитриевна",
            building=8,
            entrance=1,
            floor=3,
            room="5412",
            roles=["student"],
            phone="+79001234567",
            email="student@example.com",
            is_minor=False,
        )

    async def check_user_role(self, user_id: str, role: str) -> bool:
        return role == "student"


def get_auth_client() -> AuthClientProtocol:
    return AuthClientStub()
