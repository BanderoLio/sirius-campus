from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass
class TokenValidation:
    valid: bool
    user_id: str
    roles: list[str]
    building: str
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
    building: str
    entrance: int
    floor: int
    room: str
    roles: list[str]
    phone: str
    email: str
    is_minor: bool


class AuthClientProtocol(Protocol):
    async def validate_token(self, token: str) -> TokenValidation | None:
        ...

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        ...

    async def get_minor_students_by_entrance(
        self,
        *,
        building: str,
        entrance: int,
    ) -> list[UserInfo]:
        ...


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
            roles=["educator"],
            building="8",
            entrance=1,
            floor=3,
            room="301",
            is_minor=False,
        )

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        return UserInfo(
            user_id=user_id,
            last_name="Иванов",
            first_name="Иван",
            patronymic="Иванович",
            building="8",
            entrance=1,
            floor=3,
            room="301",
            roles=["student"],
            phone="+79001234567",
            email="student@example.com",
            is_minor=True,
        )

    async def get_minor_students_by_entrance(
        self,
        *,
        building: str,
        entrance: int,
    ) -> list[UserInfo]:
        # Stub returns test minor students for the specified entrance
        if building == "8" and entrance == 1:
            return [
                UserInfo(
                    user_id="00000000-0000-0000-0000-000000000002",
                    last_name="Петров",
                    first_name="Петр",
                    patronymic="Петрович",
                    building="8",
                    entrance=1,
                    floor=2,
                    room="201",
                    roles=["student"],
                    phone="+79001234568",
                    email="student2@example.com",
                    is_minor=True,
                ),
                UserInfo(
                    user_id="00000000-0000-0000-0000-000000000003",
                    last_name="Сидоров",
                    first_name="Сидор",
                    patronymic="Сидорович",
                    building="8",
                    entrance=1,
                    floor=3,
                    room="301",
                    roles=["student"],
                    phone="+79001234569",
                    email="student3@example.com",
                    is_minor=True,
                ),
            ]
        return []


def get_auth_client() -> AuthClientProtocol:
    return AuthClientStub()
