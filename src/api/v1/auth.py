"""
Auth API endpoints.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.auth import (
    EducatorCreate,
    EducatorResponse,
    EducatorUpdate,
    PaginatedEducatorsResponse,
    PaginatedStudentsResponse,
    PaginatedUsersResponse,
    RefreshTokenRequest,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    TokenResponse,
    UserLogin,
    UserResponse,
    UserWithProfile,
)
from src.schemas.error import AuthErrorCode, ErrorResponse
from src.services.auth import AuthService, EducatorService, StudentService, UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> uuid.UUID:
    """Get current user ID from token."""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.UNAUTHORIZED,
                    "message": "Не аутентифицирован",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    return user.id


# Authentication endpoints
@router.post(
    "/register/student",
    response_model=UserWithProfile,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "User already exists"},
    },
)
async def register_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new student."""
    auth_service = AuthService(db)

    try:
        user, student = await auth_service.register_student(data)
    except ValueError as e:
        if str(e) == AuthErrorCode.USER_ALREADY_EXISTS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error={
                        "code": AuthErrorCode.USER_ALREADY_EXISTS,
                        "message": "Пользователь с указанным email уже существует",
                        "trace_id": None,
                        "details": None,
                    }
                ).model_dump(),
            )
        raise

    # Build response
    user_response = UserResponse.model_validate(user)
    student_response = StudentResponse(
        id=student.id,
        user_id=student.user_id,
        building=student.building,
        entrance=student.entrance,
        floor=student.floor,
        room=student.room,
        is_adult=student.is_adult,
        created_at=student.created_at,
        updated_at=student.updated_at,
        phone=user.phone,
    )

    return UserWithProfile(
        user=user_response,
        profile=student_response,
        user_type="student",
    )


@router.post(
    "/register/educator",
    response_model=UserWithProfile,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse, "description": "User already exists"},
    },
)
async def register_educator(
    data: EducatorCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new educator."""
    auth_service = AuthService(db)

    try:
        user, educator = await auth_service.register_educator(data)
    except ValueError as e:
        if str(e) == AuthErrorCode.USER_ALREADY_EXISTS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ErrorResponse(
                    error={
                        "code": AuthErrorCode.USER_ALREADY_EXISTS,
                        "message": "Пользователь с указанным email уже существует",
                        "trace_id": None,
                        "details": None,
                    }
                ).model_dump(),
            )
        raise

    # Build response
    user_response = UserResponse.model_validate(user)
    educator_response = EducatorResponse.model_validate(educator)

    return UserWithProfile(
        user=user_response,
        profile=educator_response,
        user_type="educator",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login user and get tokens."""
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.login(data.email, data.password)
    except ValueError as e:
        error_code = str(e)
        if error_code == AuthErrorCode.INVALID_CREDENTIALS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorResponse(
                    error={
                        "code": AuthErrorCode.INVALID_CREDENTIALS,
                        "message": "Неверный email или пароль",
                        "trace_id": None,
                        "details": None,
                    }
                ).model_dump(),
            )
        elif error_code == AuthErrorCode.USER_INACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorResponse(
                    error={
                        "code": AuthErrorCode.USER_INACTIVE,
                        "message": "Пользователь неактивен",
                        "trace_id": None,
                        "details": None,
                    }
                ).model_dump(),
            )
        raise

    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token."""
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.refresh_tokens(data.refresh_token)
    except ValueError as e:
        error_code = str(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorResponse(
                error={
                    "code": error_code,
                    "message": "Недействительный или истекший refresh token",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    return tokens


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Logout user."""
    auth_service = AuthService(db)
    await auth_service.logout(user_id)


# User endpoints
@router.get(
    "/me",
    response_model=UserWithProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    user_service = UserService(db)
    user = await user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.USER_NOT_FOUND,
                    "message": "Пользователь не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    user_response = UserResponse.model_validate(user)

    # Determine profile type
    profile = None
    user_type = None

    if user.student_profile:
        student = user.student_profile
        profile = StudentResponse(
            id=student.id,
            user_id=student.user_id,
            building=student.building,
            entrance=student.entrance,
            floor=student.floor,
            room=student.room,
            is_adult=student.is_adult,
            created_at=student.created_at,
            updated_at=student.updated_at,
            phone=user.phone,
        )
        user_type = "student"
    elif user.educator_profile:
        profile = EducatorResponse.model_validate(user.educator_profile)
        user_type = "educator"

    return UserWithProfile(
        user=user_response,
        profile=profile,
        user_type=user_type,
    )


@router.patch(
    "/me",
    response_model=UserWithProfile,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
async def update_current_user(
    data: UserUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    user_service = UserService(db)
    user = await user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.USER_NOT_FOUND,
                    "message": "Пользователь не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    user = await user_service.update_user(user, data)

    user_response = UserResponse.model_validate(user)

    return UserWithProfile(
        user=user_response,
        profile=None,
        user_type=None,
    )


# Student endpoints
@router.get(
    "/students",
    response_model=PaginatedStudentsResponse,
)
async def list_students(
    page: int = 1,
    size: int = 20,
    building: Optional[int] = None,
    entrance: Optional[int] = None,
    floor: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List students with pagination."""
    student_service = StudentService(db)
    students, total = await student_service.list_students(
        page=page,
        size=size,
        building=building,
        entrance=entrance,
        floor=floor,
    )

    items = [
        StudentResponse(
            id=s.id,
            user_id=s.user_id,
            building=s.building,
            entrance=s.entrance,
            floor=s.floor,
            room=s.room,
            is_adult=s.is_adult,
            created_at=s.created_at,
            updated_at=s.updated_at,
            phone=s.user.phone if s.user else None,
        )
        for s in students
    ]

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedStudentsResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/students/{student_id}",
    response_model=StudentResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def get_student(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get student by ID."""
    student_service = StudentService(db)
    student = await student_service.get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.STUDENT_NOT_FOUND,
                    "message": "Студент не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    return StudentResponse(
        id=student.id,
        user_id=student.user_id,
        building=student.building,
        entrance=student.entrance,
        floor=student.floor,
        room=student.room,
        is_adult=student.is_adult,
        created_at=student.created_at,
        updated_at=student.updated_at,
        phone=student.user.phone if student.user else None,
    )


@router.patch(
    "/students/{student_id}",
    response_model=StudentResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Student not found"},
    },
)
async def update_student(
    student_id: uuid.UUID,
    data: StudentUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update student profile."""
    student_service = StudentService(db)
    student = await student_service.get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.STUDENT_NOT_FOUND,
                    "message": "Студент не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    # Check permission (only the student themselves can update)
    user_service = UserService(db)
    user = await user_service.get_user(current_user_id)

    if not user or str(user.id) != str(student.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.FORBIDDEN,
                    "message": "Нет доступа",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    student, user = await student_service.update_student(student, data, user)

    return StudentResponse(
        id=student.id,
        user_id=student.user_id,
        building=student.building,
        entrance=student.entrance,
        floor=student.floor,
        room=student.room,
        is_adult=student.is_adult,
        created_at=student.created_at,
        updated_at=student.updated_at,
        phone=user.phone,
    )


# Educator endpoints
@router.get(
    "/educators",
    response_model=PaginatedEducatorsResponse,
)
async def list_educators(
    page: int = 1,
    size: int = 20,
    is_night: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """List educators with pagination."""
    educator_service = EducatorService(db)
    educators, total = await educator_service.list_educators(
        page=page,
        size=size,
        is_night=is_night,
    )

    items = [EducatorResponse.model_validate(e) for e in educators]
    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedEducatorsResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/educators/{educator_id}",
    response_model=EducatorResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Educator not found"},
    },
)
async def get_educator(
    educator_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get educator by ID."""
    educator_service = EducatorService(db)
    educator = await educator_service.get_educator(educator_id)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.EDUCATOR_NOT_FOUND,
                    "message": "Воспитатель не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    return EducatorResponse.model_validate(educator)


@router.patch(
    "/educators/{educator_id}",
    response_model=EducatorResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Educator not found"},
    },
)
async def update_educator(
    educator_id: uuid.UUID,
    data: EducatorUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update educator profile."""
    educator_service = EducatorService(db)
    educator = await educator_service.get_educator(educator_id)

    if not educator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.EDUCATOR_NOT_FOUND,
                    "message": "Воспитатель не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    # Check permission (only the educator themselves can update)
    user_service = UserService(db)
    user = await user_service.get_user(current_user_id)

    if not user or str(user.id) != str(educator.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.FORBIDDEN,
                    "message": "Нет доступа",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    educator, user = await educator_service.update_educator(educator, data, user)

    return EducatorResponse.model_validate(educator)


# Users endpoints (admin)
@router.get(
    "/users",
    response_model=PaginatedUsersResponse,
)
async def list_users(
    page: int = 1,
    size: int = 20,
    building: Optional[int] = None,
    entrance: Optional[int] = None,
    floor: Optional[int] = None,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List users with pagination (admin endpoint)."""
    user_service = UserService(db)
    users, total = await user_service.list_users(
        page=page,
        size=size,
        building=building,
        entrance=entrance,
        floor=floor,
        role=role,
    )

    items = [UserResponse.model_validate(u) for u in users]
    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedUsersResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    user_service = UserService(db)
    user = await user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error={
                    "code": AuthErrorCode.USER_NOT_FOUND,
                    "message": "Пользователь не найден",
                    "trace_id": None,
                    "details": None,
                }
            ).model_dump(),
        )

    return UserResponse.model_validate(user)
