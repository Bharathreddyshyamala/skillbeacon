from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.repositories.refresh_token_repository import (
    create_refresh_token,
    get_refresh_token_by_hash,
    revoke_refresh_token,
)
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_id,
)
from app.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


def register_user(
    db: Session,
    request: RegisterRequest,
) -> User:
    existing_user = get_user_by_email(db, request.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = create_user(
        db=db,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
    )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc

    db.refresh(user)
    return user


def _issue_tokens(
    db: Session,
    user: User,
) -> TokenResponse:
    raw_refresh_token = generate_refresh_token()

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    create_refresh_token(
        db=db,
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=expires_at,
    )

    db.commit()

    return TokenResponse(
        access_token=create_access_token(
            user_id=user.id,
            role=user.role,
        ),
        refresh_token=raw_refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


def authenticate_user(
    db: Session,
    request: LoginRequest,
) -> TokenResponse:
    user = get_user_by_email(db, request.email)

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return _issue_tokens(db, user)


def refresh_user_tokens(
    db: Session,
    raw_refresh_token: str,
) -> TokenResponse:
    token_hash = hash_refresh_token(raw_refresh_token)

    stored_token = get_refresh_token_by_hash(
        db,
        token_hash,
    )

    now = datetime.now(timezone.utc)

    if (
        stored_token is None
        or stored_token.revoked_at is not None
        or stored_token.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user = get_user_by_id(db, stored_token.user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable",
        )

    revoke_refresh_token(stored_token)
    db.flush()

    return _issue_tokens(db, user)


def logout_user(
    db: Session,
    raw_refresh_token: str,
) -> None:
    token_hash = hash_refresh_token(raw_refresh_token)

    stored_token = get_refresh_token_by_hash(
        db,
        token_hash,
    )

    if stored_token is not None and stored_token.revoked_at is None:
        revoke_refresh_token(stored_token)
        db.commit()
