"""
Schemas package.
"""
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
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserWithProfile,
)
from src.schemas.error import (
    AuthErrorCode,
    CommonErrorCode,
    ErrorDetail,
    ErrorResponse,
)

__all__ = [
    # Auth schemas
    "UserCreate",
    "StudentCreate",
    "EducatorCreate",
    "UserUpdate",
    "StudentUpdate",
    "EducatorUpdate",
    "UserLogin",
    "RefreshTokenRequest",
    "UserResponse",
    "StudentResponse",
    "EducatorResponse",
    "TokenResponse",
    "UserWithProfile",
    "PaginatedUsersResponse",
    "PaginatedStudentsResponse",
    "PaginatedEducatorsResponse",
    # Error schemas
    "ErrorResponse",
    "ErrorDetail",
    "AuthErrorCode",
    "CommonErrorCode",
]
