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



from app.models.mentorship import (
    MentorshipStatus,
)

from app.models.user import User

from app.schemas.mentorship_schema import (
    MentorDirectoryListResponse,
    MentorshipCreateRequest,
    MentorshipListResponse,
    MentorshipRespondRequest,
    MentorshipResponse,
    MentorshipSessionCreateRequest,
    MentorshipSessionStatusRequest,
)

from app.services.mentorship_service import (
    browse_mentors,
    cancel_mentorship_request,
    change_session_status,
    complete_mentorship,
    get_mentorship_detail,
    get_my_mentorships,
    request_mentorship,
    respond_to_mentorship,
    schedule_mentorship_session,
)


router = APIRouter(
    prefix="/mentorships",
    tags=["Mentorships"],
)


# ============================================================
# Student: browse mentors
# ============================================================


@router.get(
    "/mentors",
    response_model=(
        MentorDirectoryListResponse
    ),
)
def mentor_directory(
    search: Optional[str] = Query(
        default=None
    ),

    skill_id: Optional[UUID] = Query(
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

    return browse_mentors(
        db=db,
        current_user=current_user,
        search=search,
        skill_id=skill_id,
        limit=limit,
        offset=offset,
    )


# ============================================================
# Student: send request
# ============================================================


@router.post(
    "/requests",
    response_model=(
        MentorshipResponse
    ),
    status_code=201,
)
def create_mentorship_request(
    request: MentorshipCreateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return request_mentorship(
        db,
        current_user,
        request,
    )


# ============================================================
# Student or mentor: list own
# ============================================================


@router.get(
    "/me",
    response_model=(
        MentorshipListResponse
    ),
)
def my_mentorships(
    status_filter: Optional[
        MentorshipStatus
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

    return get_my_mentorships(
        db=db,
        current_user=current_user,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


# ============================================================
# Mentor: update session
#
# Keep this before /{mentorship_id}
# ============================================================


@router.patch(
    "/sessions/{session_id}/status",
    response_model=(
        MentorshipResponse
    ),
)
def update_session_status(
    session_id: UUID,

    request: MentorshipSessionStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_session_status(
        db,
        current_user,
        session_id,
        request,
    )


# ============================================================
# Mentor: schedule session
# ============================================================


@router.post(
    "/{mentorship_id}/sessions",
    response_model=(
        MentorshipResponse
    ),
    status_code=201,
)
def create_session(
    mentorship_id: UUID,

    request: MentorshipSessionCreateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return schedule_mentorship_session(
        db,
        current_user,
        mentorship_id,
        request,
    )


# ============================================================
# Mentor: accept/reject
# ============================================================


@router.patch(
    "/{mentorship_id}/respond",
    response_model=(
        MentorshipResponse
    ),
)
def respond_to_request(
    mentorship_id: UUID,

    request: MentorshipRespondRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return respond_to_mentorship(
        db,
        current_user,
        mentorship_id,
        request,
    )


# ============================================================
# Student: cancel pending
# ============================================================


@router.patch(
    "/{mentorship_id}/cancel",
    response_model=(
        MentorshipResponse
    ),
)
def cancel_request(
    mentorship_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return cancel_mentorship_request(
        db,
        current_user,
        mentorship_id,
    )


# ============================================================
# Student or mentor: complete
# ============================================================


@router.patch(
    "/{mentorship_id}/complete",
    response_model=(
        MentorshipResponse
    ),
)
def complete_relationship(
    mentorship_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return complete_mentorship(
        db,
        current_user,
        mentorship_id,
    )


# ============================================================
# Participant: detail
#
# Keep dynamic detail last.
# ============================================================


@router.get(
    "/{mentorship_id}",
    response_model=(
        MentorshipResponse
    ),
)
def mentorship_detail(
    mentorship_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_mentorship_detail(
        db,
        current_user,
        mentorship_id,
    )