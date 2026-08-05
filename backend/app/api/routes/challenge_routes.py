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
    ChallengeDifficulty,
    ChallengeSubmissionStatus,
    ChallengeType,
)

from app.models.user import User

from app.schemas.challenge_schema import (
    ChallengeCreateRequest,
    ChallengeListResponse,
    ChallengeResponse,
    ChallengeStatusRequest,
    ChallengeSubmissionCreateRequest,
    ChallengeSubmissionReviewRequest,
    ChallengeUpdateRequest,
    EmployerChallengeSubmissionListResponse,
    EmployerChallengeSubmissionResponse,
    StudentChallengeSubmissionListResponse,
    StudentChallengeSubmissionResponse,
)

from app.services.challenge_service import (
    browse_challenges,
    change_challenge_status,
    create_new_challenge,
    get_challenge_submissions,
    get_my_challenges,
    get_my_challenge_submissions,
    get_open_challenge,
    review_challenge_submission,
    submit_challenge_solution,
    update_existing_challenge,
)


router = APIRouter(
    tags=["Challenges"],
)







@router.get(
    "/challenges",
    response_model=ChallengeListResponse,
)
def list_challenges_route(
    search: Optional[str] = Query(
        default=None
    ),

    challenge_type: Optional[
        ChallengeType
    ] = Query(
        default=None
    ),

    difficulty: Optional[
        ChallengeDifficulty
    ] = Query(
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

    return browse_challenges(
        db=db,
        current_user=current_user,
        search=search,
        challenge_type=challenge_type,
        difficulty=difficulty,
        skill_id=skill_id,
        limit=limit,
        offset=offset,
    )









@router.get(
    "/challenges/me",
    response_model=list[
        ChallengeResponse
    ],
)
def my_challenges_route(
    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_my_challenges(
        db,
        current_user,
    )












@router.get(
    "/challenge-submissions/me",
    response_model=(
        StudentChallengeSubmissionListResponse
    ),
)
def my_submissions_route(
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

    return get_my_challenge_submissions(
        db,
        current_user,
        limit,
        offset,
    )







@router.post(
    "/challenges",
    response_model=ChallengeResponse,
    status_code=201,
)
def create_challenge_route(
    request: ChallengeCreateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return create_new_challenge(
        db,
        current_user,
        request,
    )







@router.get(
    "/challenges/{challenge_id}/submissions",
    response_model=(
        EmployerChallengeSubmissionListResponse
    ),
)
def challenge_submissions_route(
    challenge_id: UUID,

    status_filter: Optional[
        ChallengeSubmissionStatus
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

    return get_challenge_submissions(
        db,
        current_user,
        challenge_id,
        status_filter,
        limit,
        offset,
    )







@router.post(
    "/challenges/{challenge_id}/submissions",
    response_model=(
        StudentChallengeSubmissionResponse
    ),
    status_code=201,
)
def submit_challenge_route(
    challenge_id: UUID,

    request: ChallengeSubmissionCreateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return submit_challenge_solution(
        db,
        current_user,
        challenge_id,
        request,
    )







@router.patch(
    "/challenge-submissions/{submission_id}/review",
    response_model=(
        EmployerChallengeSubmissionResponse
    ),
)
def review_submission_route(
    submission_id: UUID,

    request: ChallengeSubmissionReviewRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return review_challenge_submission(
        db,
        current_user,
        submission_id,
        request,
    )







@router.put(
    "/challenges/{challenge_id}",
    response_model=ChallengeResponse,
)
def update_challenge_route(
    challenge_id: UUID,

    request: ChallengeUpdateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return update_existing_challenge(
        db,
        current_user,
        challenge_id,
        request,
    )







@router.patch(
    "/challenges/{challenge_id}/status",
    response_model=ChallengeResponse,
)
def challenge_status_route(
    challenge_id: UUID,

    request: ChallengeStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_challenge_status(
        db,
        current_user,
        challenge_id,
        request,
    )









@router.get(
    "/challenges/{challenge_id}",
    response_model=ChallengeResponse,
)
def challenge_detail_route(
    challenge_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_open_challenge(
        db,
        current_user,
        challenge_id,
    )