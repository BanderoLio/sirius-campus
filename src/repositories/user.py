"""
User repository for data access.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.database import Educator, Role, Student, User, UserRole


class UserRepository:
    """Repository for user data access."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.student_profile),
                selectinload(User.educator_profile),
                selectinload(User.roles),
            )
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.student_profile),
                selectinload(User.educator_profile),
                selectinload(User.roles),
            )
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        patronymic: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            phone=phone,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update user."""
        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete user."""
        await self.db.delete(user)
        await self.db.flush()

    async def list_users(
        self,
        page: int = 1,
        size: int = 20,
        building: Optional[int] = None,
        entrance: Optional[int] = None,
        floor: Optional[int] = None,
        role: Optional[Role] = None,
    ) -> tuple[list[User], int]:
        """List users with pagination and filters."""
        query = select(User).options(
            selectinload(User.student_profile),
            selectinload(User.educator_profile),
            selectinload(User.roles),
        )

        # Apply building/entrance/floor filters via student profile
        if building or entrance or floor:
            query = query.join(User.student_profile)
            if building:
                query = query.where(Student.building == building)
            if entrance:
                query = query.where(Student.entrance == entrance)
            if floor:
                query = query.where(Student.floor == floor)

        # Apply role filter
        if role:
            query = query.join(User.roles).where(UserRole.role == role)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(User.created_at.desc())

        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def add_role(self, user: User, role: Role) -> UserRole:
        """Add role to user."""
        user_role = UserRole(user_id=user.id, role=role)
        self.db.add(user_role)
        await self.db.flush()
        return user_role

    async def remove_role(self, user: User, role: Role) -> None:
        """Remove role from user."""
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user.id, UserRole.role == role
            )
        )
        user_role = result.scalar_one_or_none()
        if user_role:
            await self.db.delete(user_role)
            await self.db.flush()

    async def get_user_roles(self, user: User) -> list[str]:
        """Get user roles as list of strings."""
        return [role.value for role in user.roles]


class StudentRepository:
    """Repository for student data access."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, student_id: uuid.UUID) -> Optional[Student]:
        """Get student by ID."""
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.user))
            .where(Student.id == student_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Student]:
        """Get student by user ID."""
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.user))
            .where(Student.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: uuid.UUID,
        building: int,
        entrance: int,
        floor: int,
        room: int,
        is_adult: bool = False,
    ) -> Student:
        """Create a new student profile."""
        student = Student(
            user_id=user_id,
            building=building,
            entrance=entrance,
            floor=floor,
            room=room,
            is_adult=is_adult,
        )
        self.db.add(student)
        await self.db.flush()
        await self.db.refresh(student)
        return student

    async def update(self, student: Student) -> Student:
        """Update student profile."""
        student.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(student)
        return student

    async def delete(self, student: Student) -> None:
        """Delete student profile."""
        await self.db.delete(student)
        await self.db.flush()

    async def list_students(
        self,
        page: int = 1,
        size: int = 20,
        building: Optional[int] = None,
        entrance: Optional[int] = None,
        floor: Optional[int] = None,
    ) -> tuple[list[Student], int]:
        """List students with pagination and filters."""
        query = select(Student).options(selectinload(Student.user))

        if building:
            query = query.where(Student.building == building)
        if entrance:
            query = query.where(Student.entrance == entrance)
        if floor:
            query = query.where(Student.floor == floor)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(Student.created_at.desc())

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        return students, total


class EducatorRepository:
    """Repository for educator data access."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, educator_id: uuid.UUID) -> Optional[Educator]:
        """Get educator by ID."""
        result = await self.db.execute(
            select(Educator)
            .options(selectinload(Educator.user))
            .where(Educator.id == educator_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Educator]:
        """Get educator by user ID."""
        result = await self.db.execute(
            select(Educator)
            .options(selectinload(Educator.user))
            .where(Educator.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: uuid.UUID,
        is_night: bool = False,
    ) -> Educator:
        """Create a new educator profile."""
        educator = Educator(
            user_id=user_id,
            is_night=is_night,
        )
        self.db.add(educator)
        await self.db.flush()
        await self.db.refresh(educator)
        return educator

    async def update(self, educator: Educator) -> Educator:
        """Update educator profile."""
        educator.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(educator)
        return educator

    async def delete(self, educator: Educator) -> None:
        """Delete educator profile."""
        await self.db.delete(educator)
        await self.db.flush()

    async def list_educators(
        self,
        page: int = 1,
        size: int = 20,
        is_night: Optional[bool] = None,
    ) -> tuple[list[Educator], int]:
        """List educators with pagination and filters."""
        query = select(Educator).options(selectinload(Educator.user))

        if is_night is not None:
            query = query.where(Educator.is_night == is_night)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(Educator.created_at.desc())

        result = await self.db.execute(query)
        educators = list(result.scalars().all())

        return educators, total


class RefreshTokenRepository:
    """Repository for refresh token data access."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        token: str,
        expires_at: datetime,
    ) -> "RefreshToken":
        """Create a new refresh token."""
        from src.models.database import RefreshToken

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        await self.db.flush()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_by_token(self, token: str) -> Optional["RefreshToken"]:
        """Get refresh token by token string."""
        result = await self.db.execute(
            select(RefreshToken)
            .options(selectinload(RefreshToken.user))
            .where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: "RefreshToken") -> None:
        """Revoke a refresh token."""
        token.is_revoked = True
        await self.db.flush()

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revoke all refresh tokens for a user."""
        from src.models.database import RefreshToken

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,  # noqa: E712
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.is_revoked = True
        await self.db.flush()

    async def delete_expired(self) -> int:
        """Delete expired refresh tokens."""
        from src.models.database import RefreshToken

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        tokens = result.scalars().all()
        count = len(tokens)
        for token in tokens:
            await self.db.delete(token)
        await self.db.flush()
        return count
