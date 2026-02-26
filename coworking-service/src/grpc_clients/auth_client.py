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


STUB_PROFILES: dict[str, tuple[str, list[str], str, str, str]] = {
    "student": (
        "00000000-0000-0000-0000-000000000001",
        ["student"],
        "Тарасенко", "Алиса", "Дмитриевна",
    ),
    "educator": (
        "00000000-0000-0000-0000-000000000002",
        ["educator", "educator_head"],
        "Иванов", "Пётр", "Сергеевич",
    ),
    "admin": (
        "00000000-0000-0000-0000-000000000003",
        ["admin", "educator", "educator_head"],
        "Сидорова", "Мария", "Андреевна",
    ),
}


def _parse_stub_token(token: str) -> tuple[str, list[str], str, str, str]:
    """Token format: 'role:anything' or just 'anything' (defaults to student+educator)."""
    key = token.split(":", 1)[0] if ":" in token else ""
    if key in STUB_PROFILES:
        return STUB_PROFILES[key]
    return STUB_PROFILES["student"][0], ["student", "educator"], "Тарасенко", "Алиса", "Дмитриевна"


class AuthClientStub:
    """Stub for development when auth-service is not available."""

    async def validate_token(self, token: str) -> TokenValidation | None:
        if not token or token == "Bearer":
            return None
        token_clean = token.replace("Bearer ", "").strip()
        if not token_clean:
            return None
        user_id, roles, *_ = _parse_stub_token(token_clean)
        return TokenValidation(
            valid=True,
            user_id=user_id,
            roles=roles,
            building=8,
            entrance=1,
            floor=3,
            room="5142",
            is_minor=False,
        )

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        for uid, roles, last, first, patr in STUB_PROFILES.values():
            if uid == user_id:
                return UserInfo(
                    user_id=uid, last_name=last, first_name=first, patronymic=patr,
                    building=8, entrance=1, floor=3, room="5412",
                    roles=roles, phone="+79001234567", email="dev@example.com",
                    is_minor=False,
                )
        return UserInfo(
            user_id=user_id, last_name="Тарасенко", first_name="Алиса", patronymic="Дмитриевна",
            building=8, entrance=1, floor=3, room="5412",
            roles=["student"], phone="+79001234567", email="dev@example.com",
            is_minor=False,
        )

    async def check_user_role(self, user_id: str, role: str) -> bool:
        for uid, roles, *_ in STUB_PROFILES.values():
            if uid == user_id:
                return role in roles
        return role == "student"


def get_auth_client() -> AuthClientProtocol:
    return AuthClientStub()
