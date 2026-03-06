"""
Auth service for business logic.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from src.models.database import Role, Student, User
from src.repositories.user import (
    EducatorRepository,
    RefreshTokenRepository,
    StudentRepository,
    UserRepository,
)
from src.schemas.auth import (
    EducatorCreate,
    EducatorUpdate,
    StudentCreate,
    StudentUpdate,
    TokenResponse,
    UserCreate,
    UserUpdate,
)
from src.schemas.error import AuthErrorCode


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_token_repo = RefreshTokenRepository(db)

    async def register_student(self, data: StudentCreate) -> tuple[User, Student]:
        """Register a new student."""
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise ValueError(AuthErrorCode.USER_ALREADY_EXISTS)

        # Create user
        user = await self.user_repo.create(
            email=data.email,
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            patronymic=data.patronymic,
            phone=data.phone,
        )

        # Add student role
        await self.user_repo.add_role(user, Role.STUDENT)

        # Create student profile
        student_repo = StudentRepository(self.db)
        student = await student_repo.create(
            user_id=user.id,
            building=data.building,
            entrance=data.entrance,
            floor=data.floor,
            room=data.room,
            is_adult=data.is_adult,
        )

        await self.db.commit()
        return user, student

    async def register_educator(
        self, data: EducatorCreate
    ) -> tuple[User, "Educator"]:
        """Register a new educator."""
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise ValueError(AuthErrorCode.USER_ALREADY_EXISTS)

        # Create user
        user = await self.user_repo.create(
            email=data.email,
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            patronymic=data.patronymic,
            phone=data.phone,
        )

        # Add educator role
        await self.user_repo.add_role(user, Role.EDUCATOR)

        # Create educator profile
        educator_repo = EducatorRepository(self.db)
        educator = await educator_repo.create(
            user_id=user.id,
            is_night=data.is_night,
        )

        await self.db.commit()
        return user, educator

    async def login(self, email: str, password: str) -> TokenResponse:
        """Login user and return tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError(AuthErrorCode.INVALID_CREDENTIALS)

        if not verify_password(password, user.password_hash):
            raise ValueError(AuthErrorCode.INVALID_CREDENTIALS)

        if not user.is_active:
            raise ValueError(AuthErrorCode.USER_INACTIVE)

        # Get user roles
        roles = await self.user_repo.get_user_roles(user)

        # Get student profile for additional claims
        building: Optional[str] = None
        entrance: Optional[int] = None
        floor: Optional[int] = None
        room: Optional[str] = None
        is_minor = False

        if user.student_profile:
            building = str(user.student_profile.building)
            entrance = user.student_profile.entrance
            floor = user.student_profile.floor
            room = str(user.student_profile.room)
            is_minor = not user.student_profile.is_adult

        # Create tokens
        access_token, _ = create_access_token(
            subject=str(user.id),
            roles=roles,
            building=building,
            entrance=entrance,
            floor=floor,
            room=room,
            is_minor=is_minor,
        )

        refresh_token, refresh_expires = create_refresh_token(
            subject=str(user.id)
        )

        # Save refresh token
        await self.refresh_token_repo.create(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_expires,
        )

        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        # Validate refresh token
        token_data = decode_token(refresh_token)
        if not token_data:
            raise ValueError(AuthErrorCode.INVALID_TOKEN)

        if token_data.get("type") != "refresh":
            raise ValueError(AuthErrorCode.INVALID_TOKEN)

        # Get refresh token from database
        stored_token = await self.refresh_token_repo.get_by_token(refresh_token)
        if not stored_token:
            raise ValueError(AuthErrorCode.REFRESH_TOKEN_INVALID)

        if stored_token.is_revoked:
            raise ValueError(AuthErrorCode.TOKEN_REVOKED)

        if stored_token.expires_at < datetime.now(timezone.utc):
            raise ValueError(AuthErrorCode.TOKEN_EXPIRED)

        # Get user
        user = await self.user_repo.get_by_id(stored_token.user_id)
        if not user or not user.is_active:
            raise ValueError(AuthErrorCode.USER_NOT_FOUND)

        # Revoke old refresh token
        await self.refresh_token_repo.revoke(stored_token)

        # Get user roles
        roles = await self.user_repo.get_user_roles(user)

        # Get student profile for additional claims
        building: Optional[str] = None
        entrance: Optional[int] = None
        floor: Optional[int] = None
        room: Optional[str] = None
        is_minor = False

        if user.student_profile:
            building = str(user.student_profile.building)
            entrance = user.student_profile.entrance
            floor = user.student_profile.floor
            room = str(user.student_profile.room)
            is_minor = not user.student_profile.is_adult

        # Create new tokens
        access_token, _ = create_access_token(
            subject=str(user.id),
            roles=roles,
            building=building,
            entrance=entrance,
            floor=floor,
            room=room,
            is_minor=is_minor,
        )

        new_refresh_token, refresh_expires = create_refresh_token(
            subject=str(user.id)
        )

        # Save new refresh token
        await self.refresh_token_repo.create(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=refresh_expires,
        )

        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(self, user_id: uuid.UUID) -> None:
        """Logout user by revoking all refresh tokens."""
        await self.refresh_token_repo.revoke_all_user_tokens(user_id)
        await self.db.commit()

    async def validate_token(self, token: str) -> Optional[dict]:
        """Validate access token and return payload."""
        payload = decode_token(token)
        if not payload:
            return None

        # Check if it's not a refresh token
        if payload.get("type") == "refresh":
            return None

        return payload

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = await self.validate_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return await self.user_repo.get_by_id(uuid.UUID(user_id))


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repo.get_by_email(email)

    async def update_user(
        self, user: User, data: UserUpdate
    ) -> User:
        """Update user."""
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.patronymic is not None:
            user.patronymic = data.patronymic
        if data.phone is not None:
            user.phone = data.phone
        if data.password is not None:
            user.password_hash = get_password_hash(data.password)

        return await self.user_repo.update(user)

    async def list_users(
        self,
        page: int = 1,
        size: int = 20,
        building: Optional[int] = None,
        entrance: Optional[int] = None,
        floor: Optional[int] = None,
        role: Optional[str] = None,
    ) -> tuple[list[User], int]:
        """List users with pagination and filters."""
        role_enum = Role(role) if role else None
        return await self.user_repo.list_users(
            page=page,
            size=size,
            building=building,
            entrance=entrance,
            floor=floor,
            role=role_enum,
        )


class StudentService:
    """Service for student operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.user_repo = UserRepository(db)

    async def get_student(self, student_id: uuid.UUID) -> Optional[Student]:
        """Get student by ID."""
        return await self.student_repo.get_by_id(student_id)

    async def get_student_by_user_id(self, user_id: uuid.UUID) -> Optional[Student]:
        """Get student by user ID."""
        return await self.student_repo.get_by_user_id(user_id)

    async def update_student(
        self, student: Student, data: StudentUpdate, user: User
    ) -> tuple[Student, User]:
        """Update student profile."""
        # Update user fields if provided
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.patronymic is not None:
            user.patronymic = data.patronymic
        if data.phone is not None:
            user.phone = data.phone
        if data.password is not None:
            user.password_hash = get_password_hash(data.password)

        await self.user_repo.update(user)

        # Update student fields if provided
        if data.building is not None:
            student.building = data.building
        if data.entrance is not None:
            student.entrance = data.entrance
        if data.floor is not None:
            student.floor = data.floor
        if data.room is not None:
            student.room = data.room
        if data.is_adult is not None:
            student.is_adult = data.is_adult

        student = await self.student_repo.update(student)
        await self.db.commit()

        return student, user

    async def list_students(
        self,
        page: int = 1,
        size: int = 20,
        building: Optional[int] = None,
        entrance: Optional[int] = None,
        floor: Optional[int] = None,
    ) -> tuple[list[Student], int]:
        """List students with pagination and filters."""
        return await self.student_repo.list_students(
            page=page,
            size=size,
            building=building,
            entrance=entrance,
            floor=floor,
        )


class EducatorService:
    """Service for educator operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.educator_repo = EducatorRepository(db)
        self.user_repo = UserRepository(db)

    async def get_educator(self, educator_id: uuid.UUID) -> Optional["Educator"]:
        """Get educator by ID."""
        return await self.educator_repo.get_by_id(educator_id)

    async def get_educator_by_user_id(self, user_id: uuid.UUID) -> Optional["Educator"]:
        """Get educator by user ID."""
        return await self.educator_repo.get_by_user_id(user_id)

    async def update_educator(
        self, educator: "Educator", data: EducatorUpdate, user: User
    ) -> tuple["Educator", User]:
        """Update educator profile."""
        # Update user fields if provided
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        if data.patronymic is not None:
            user.patronymic = data.patronymic
        if data.phone is not None:
            user.phone = data.phone
        if data.password is not None:
            user.password_hash = get_password_hash(data.password)

        await self.user_repo.update(user)

        # Update educator fields if provided
        if data.is_night is not None:
            educator.is_night = data.is_night

        educator = await self.educator_repo.update(educator)
        await self.db.commit()

        return educator, user

    async def list_educators(
        self,
        page: int = 1,
        size: int = 20,
        is_night: Optional[bool] = None,
    ) -> tuple[list["Educator"], int]:
        """List educators with pagination and filters."""
        return await self.educator_repo.list_educators(
            page=page,
            size=size,
            is_night=is_night,
        )
