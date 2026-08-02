from typing import List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.skill_schema import (
    EvidenceCreateRequest,
    SkillCreateRequest,
    SkillResponse,
    UserSkillCreateRequest,
    UserSkillResponse,
    UserSkillUpdateRequest,
    VerificationCreateRequest,
    EvidenceReviewItem,
)
from app.services.skill_service import (
    add_my_skill,
    add_skill_evidence,
    create_catalog_skill,
    get_my_skills,
    list_skill_catalog,
    remove_my_skill,
    update_my_skill,
    verify_evidence,
    get_pending_evidence,

)


router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
)


@router.get(
    "",
    response_model=List[SkillResponse],
)
def get_skills(
    db: Session = Depends(get_db),
):
    return list_skill_catalog(db)


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill(
    request: SkillCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return create_catalog_skill(
        db,
        current_user,
        request,
    )


@router.get(
    "/me",
    response_model=List[UserSkillResponse],
)
def get_current_user_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_my_skills(
        db,
        current_user,
    )


@router.post(
    "/me",
    response_model=UserSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_current_user_skill(
    request: UserSkillCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return add_my_skill(
        db,
        current_user,
        request,
    )


@router.put(
    "/me/{user_skill_id}",
    response_model=UserSkillResponse,
)
def update_current_user_skill(
    user_skill_id: UUID,
    request: UserSkillUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return update_my_skill(
        db,
        current_user,
        user_skill_id,
        request,
    )


@router.delete(
    "/me/{user_skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_current_user_skill(
    user_skill_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    remove_my_skill(
        db,
        current_user,
        user_skill_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.post(
    "/me/{user_skill_id}/evidence",
    response_model=UserSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill_evidence(
    user_skill_id: UUID,
    request: EvidenceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return add_skill_evidence(
        db,
        current_user,
        user_skill_id,
        request,
    )


@router.post(
    "/evidence/{evidence_id}/verify",
    response_model=UserSkillResponse,
)
def verify_skill_evidence(
    evidence_id: UUID,
    request: VerificationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return verify_evidence(
        db,
        current_user,
        evidence_id,
        request,
    )

@router.get(
    "/evidence/pending",
    response_model=List[
        EvidenceReviewItem
    ],
)
def get_evidence_pending_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_pending_evidence(
        db,
        current_user,
    )