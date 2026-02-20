"""
Auth placeholder: extract user_id and roles from Bearer token (JWT payload without verification).
TODO: Replace with auth-service gRPC ValidateToken when available; return 401 on invalid token.
"""
import base64
import json
from typing import Tuple

# Optional: use PyJWT for proper decode (still unverified for stub)
try:
    import jwt as pyjwt
    _HAS_JWT = True
except ImportError:
    _HAS_JWT = False


def _decode_jwt_payload_unverified(token: str) -> dict | None:
    if _HAS_JWT:
        try:
            return pyjwt.decode(token, options={"verify_signature": False})
        except Exception:
            pass
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        raw = base64.urlsafe_b64decode(payload_b64)
        return json.loads(raw)
    except Exception:
        return None


# Dev stub: accept this token as a valid user when JWT decode fails (e.g. "dev-token" from frontend MVP).
DEV_TOKEN_USER_ID = "00000000-0000-0000-0000-000000000001"
DEV_TOKEN_ROLES = ["student", "educator"]


def get_user_from_authorization(authorization: str | None) -> Tuple[str, list[str]] | None:
    """
    Returns (user_id, roles) if Authorization header is valid, else None.
    Expects: Authorization: Bearer <jwt>.
    For development, also accepts Bearer dev-token (any non-JWT) as a fixed dev user.
    """
    if not authorization or not authorization.strip().lower().startswith("bearer "):
        return None
    token = authorization[7:].strip()
    if not token:
        return None
    payload = _decode_jwt_payload_unverified(token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            roles_raw = payload.get("roles")
            if isinstance(roles_raw, list):
                roles = [str(r) for r in roles_raw]
            elif isinstance(roles_raw, str):
                roles = [r.strip() for r in roles_raw.split(",") if r.strip()]
            else:
                roles = []
            return str(user_id), roles
    # Dev: accept any non-JWT token (e.g. "dev-token") as fixed dev user
    return DEV_TOKEN_USER_ID, list(DEV_TOKEN_ROLES)
