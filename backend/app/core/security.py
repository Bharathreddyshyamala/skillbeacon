from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any, Dict, Optional
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, UserRole
from app.repositories.profile_repository import create_profile_for_user
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
)


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: UUID,
    role: UserRole,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "role": role.value,
        "type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Token is not an access token")

    return payload


def generate_refresh_token() -> str:
    return token_urlsafe(48)


def hash_refresh_token(refresh_token: str) -> str:
    return sha256(refresh_token.encode("utf-8")).hexdigest()


def validate_neon_session(
    db: Session,
    token: str,
) -> Optional[Dict[str, Any]]:
    """
    Validate a Neon Auth (Managed Better Auth) session token directly against
    the neon_auth schema in the database.
    """
    if not token or not isinstance(token, str):
        return None

    cleaned_token = token.strip()
    if cleaned_token.startswith("s%3A"):
        cleaned_token = cleaned_token[4:]
    elif cleaned_token.startswith("s:"):
        cleaned_token = cleaned_token[2:]

    token_candidate = cleaned_token.split(".")[0] if "." in cleaned_token else cleaned_token

    try:
        query = text(
            """
            SELECT s.id AS session_id,
                   s."userId" AS user_id,
                   s."expiresAt" AS expires_at,
                   u.email AS email,
                   u.name AS name,
                   u.role AS role
            FROM neon_auth.session s
            JOIN neon_auth."user" u ON s."userId" = u.id
            WHERE s.token = :token
               OR s.token = :candidate
               OR s.token = :cleaned
            LIMIT 1
            """
        )
        row = db.execute(
            query,
            {
                "token": token.strip(),
                "candidate": token_candidate.strip(),
                "cleaned": cleaned_token.strip(),
            },
        ).mappings().first()

        if not row:
            return None

        expires_at = row["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            return None

        return {
            "neon_user_id": row["user_id"],
            "email": row["email"],
            "name": row["name"],
            "role": row["role"],
        }
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Error validating neon session: %s", exc)
        return None


def get_or_create_user_from_neon(
    db: Session,
    neon_user_data: Dict[str, Any],
    desired_role: Optional[UserRole] = None,
) -> User:
    """
    Find or create a local SkillBeacon domain User linked to the authenticated
    Neon Auth user email.
    """
    email = neon_user_data["email"].strip().lower()
    user = get_user_by_email(db, email)

    if user is not None:
        return user

    # Map role if available, or use requested/default role
    role_str = (neon_user_data.get("role") or "").lower()
    if desired_role:
        assigned_role = desired_role
    elif role_str in {r.value for r in UserRole}:
        assigned_role = UserRole(role_str)
    else:
        assigned_role = UserRole.STUDENT

    user = create_user(
        db=db,
        email=email,
        password_hash=None,
        role=assigned_role,
    )
    user.is_verified = True

    try:
        if assigned_role in {UserRole.STUDENT, UserRole.EMPLOYER, UserRole.MENTOR}:
            create_profile_for_user(db, user)
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return user



