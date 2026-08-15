from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user


from app.models.challenge import (
    ChallengeStatus,
)

from app.models.opportunity import (
    OpportunityStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.schemas.admin_schema import (
    AdminAuditLogListResponse,
    AdminChallengeListResponse,
    AdminChallengeStatusRequest,
    AdminDashboardResponse,
    AdminOpportunityListResponse,
    AdminOpportunityStatusRequest,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserStatusRequest,
    AdminUserVerificationRequest,
)

from app.services.admin_service import (
    change_user_active_status,
    change_user_verification,
    get_admin_audit_logs,
    get_admin_challenges,
    get_admin_dashboard,
    get_admin_opportunities,
    get_admin_user,
    get_admin_users,
    moderate_challenge_status,
    moderate_opportunity_status,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# ============================================================
# Dashboard
# ============================================================


@router.get(
    "/dashboard",
    response_model=(
        AdminDashboardResponse
    ),
)
def admin_dashboard(
    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_admin_dashboard(
        db,
        current_user,
    )


# ============================================================
# Users
# ============================================================


@router.get(
    "/users",
    response_model=(
        AdminUserListResponse
    ),
)
def admin_users(
    search: Optional[str] = Query(
        default=None
    ),

    role: Optional[
        UserRole
    ] = Query(
        default=None
    ),

    is_active: Optional[
        bool
    ] = Query(
        default=None
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_admin_users(
        db=db,
        current_user=current_user,
        search=search,
        role=role,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/users/{user_id}",
    response_model=(
        AdminUserResponse
    ),
)
def admin_user_detail(
    user_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_admin_user(
        db,
        current_user,
        user_id,
    )


@router.patch(
    "/users/{user_id}/status",
    response_model=(
        AdminUserResponse
    ),
)
def admin_user_status(
    user_id: UUID,

    request: AdminUserStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_user_active_status(
        db,
        current_user,
        user_id,
        request,
    )


@router.patch(
    "/users/{user_id}/verification",
    response_model=(
        AdminUserResponse
    ),
)
def admin_user_verification(
    user_id: UUID,

    request: AdminUserVerificationRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_user_verification(
        db,
        current_user,
        user_id,
        request,
    )


# ============================================================
# Opportunities
# ============================================================


@router.get(
    "/opportunities",
    response_model=(
        AdminOpportunityListResponse
    ),
)
def admin_opportunities(
    search: Optional[str] = Query(
        default=None
    ),

    status_filter: Optional[
        OpportunityStatus
    ] = Query(
        default=None,
        alias="status",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_admin_opportunities(
        db=db,
        current_user=current_user,
        search=search,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/opportunities/{opportunity_id}/status",
)
def admin_opportunity_status(
    opportunity_id: UUID,

    request: AdminOpportunityStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return moderate_opportunity_status(
        db,
        current_user,
        opportunity_id,
        request,
    )


# ============================================================
# Challenges
# ============================================================


@router.get(
    "/challenges",
    response_model=(
        AdminChallengeListResponse
    ),
)
def admin_challenges(
    search: Optional[str] = Query(
        default=None
    ),

    status_filter: Optional[
        ChallengeStatus
    ] = Query(
        default=None,
        alias="status",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_admin_challenges(
        db=db,
        current_user=current_user,
        search=search,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/challenges/{challenge_id}/status",
)
def admin_challenge_status(
    challenge_id: UUID,

    request: AdminChallengeStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return moderate_challenge_status(
        db,
        current_user,
        challenge_id,
        request,
    )


# ============================================================
# Audit Logs
# ============================================================


@router.get(
    "/audit-logs",
    response_model=(
        AdminAuditLogListResponse
    ),
)
def admin_audit_logs(
    action: Optional[str] = Query(
        default=None
    ),

    target_type: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_admin_audit_logs(
        db=db,
        current_user=current_user,
        action=action,
        target_type=target_type,
        limit=limit,
        offset=offset,
    )