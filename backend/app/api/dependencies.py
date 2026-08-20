from typing import Callable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    decode_access_token,
    get_or_create_user_from_neon,
    validate_neon_session,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import get_user_by_email, get_user_by_id


bearer_scheme = HTTPBearer(auto_error=False)


def extract_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials],
) -> Optional[str]:
    """
    Extract token from Authorization header or Better Auth session cookies.
    """
    if credentials and credentials.credentials:
        return credentials.credentials.strip()

    # Check cookies used by Better Auth / Neon Auth
    session_cookie = (
        request.cookies.get("better-auth.session_token")
        or request.cookies.get("__Secure-better-auth.session_token")
        or request.cookies.get("neon-auth.session_token")
    )
    if session_cookie:
        return session_cookie.strip()

    # Check custom header if provided
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return None


def resolve_local_user(db: Session, identifier: Optional[str]) -> Optional[User]:
    """
    Resolve a user by email or UUID identifier for local development.
    """
    if not identifier:
        return None

    cleaned = identifier.strip()
    if "@" in cleaned:
        return get_user_by_email(db, cleaned)

    try:
        return get_user_by_id(db, UUID(cleaned))
    except (ValueError, TypeError):
        return None


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session / access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    raw_token = extract_token_from_request(request, credentials)

    # 1. Local profile identity resolution (X-User-Id, X-User-Email, or Bearer <email|uuid>)
    if settings.is_local_profile:
        local_identifier = (
            request.headers.get("X-User-Id")
            or request.headers.get("X-User-Email")
            or raw_token
        )
        user = resolve_local_user(db, local_identifier)
        if user is not None:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive",
                )
            return user

    if not raw_token:
        raise credentials_exception

    # 1. Try validating as a Neon Auth (Better Auth) session token
    neon_user = validate_neon_session(db, raw_token)
    if neon_user is not None:
        user = get_or_create_user_from_neon(db, neon_user)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        return user

    # 2. Fallback: Try decoding as custom JWT access token
    try:
        payload = decode_access_token(raw_token)
        user_id_text = payload.get("sub")

        if not user_id_text:
            raise credentials_exception

        user_id = UUID(user_id_text)
    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def require_roles(*allowed_roles: UserRole) -> Callable:
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role in allowed_roles:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    return role_checker


