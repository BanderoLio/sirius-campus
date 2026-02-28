"""
JWT and security utilities.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import get_settings
from src.models.database import Role, Student, User

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    roles: list[str],
    building: Optional[str] = None,
    entrance: Optional[int] = None,
    floor: Optional[int] = None,
    room: Optional[str] = None,
    is_minor: bool = False,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, datetime]:
    """
    Create JWT access token.

    Args:
        subject: User ID
        roles: List of user roles
        building: Building number (for students)
        entrance: Entrance number (for students)
        floor: Floor number (for students)
        room: Room number (for students)
        is_minor: Whether user is minor (for students)
        expires_delta: Custom expiration delta

    Returns:
        Tuple of (token, expiration datetime)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: dict[str, Any] = {
        "sub": subject,
        "roles": roles,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
    }

    # Add student-specific claims
    if building:
        to_encode["building"] = building
    if entrance:
        to_encode["entrance"] = entrance
    if floor:
        to_encode["floor"] = floor
    if room:
        to_encode["room"] = room
    if is_minor is not None:
        to_encode["is_minor"] = is_minor

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt, expire


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, datetime]:
    """
    Create JWT refresh token.

    Args:
        subject: User ID
        expires_delta: Custom expiration delta

    Returns:
        Tuple of (token, expiration datetime)
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt, expire


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from token."""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired."""
    payload = decode_token(token)
    if not payload:
        return True
    exp = payload.get("exp")
    if not exp:
        return True
    return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
