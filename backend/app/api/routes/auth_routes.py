from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth_schema import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    SyncNeonSessionRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    logout_user,
    refresh_user_tokens,
    register_user,
    sync_neon_user_session,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/sync-session",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def sync_session(
    request: SyncNeonSessionRequest,
    db: Session = Depends(get_db),
) -> User:
    """
    Sync an authenticated Neon Auth session with the local SkillBeacon User
    domain model, ensuring role profiles are created.
    """
    return sync_neon_user_session(
        db=db,
        session_token=request.session_token,
        desired_role=request.role,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> User:
    return register_user(db, request)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return authenticate_user(db, request)


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return refresh_user_tokens(db, request.refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    logout_user(db, request.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
