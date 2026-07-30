from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.profile_schema import (
    ProfileEnvelope,
    ProfileUpdateRequest,
)
from app.services.profile_service import (
    get_or_create_my_profile,
    get_public_profile,
    update_my_profile,
    upload_student_resume,
)


router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)


@router.get(
    "/me",
    response_model=ProfileEnvelope,
)
def read_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileEnvelope:
    return get_or_create_my_profile(db, current_user)


@router.put(
    "/me",
    response_model=ProfileEnvelope,
)
def update_current_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileEnvelope:
    return update_my_profile(
        db,
        current_user,
        request,
    )


@router.post(
    "/me/resume",
    response_model=ProfileEnvelope,
)
async def upload_resume(
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileEnvelope:
    return await upload_student_resume(
        db,
        current_user,
        resume,
    )


@router.get(
    "/{user_id}",
    response_model=ProfileEnvelope,
)
def read_public_profile(
    user_id: UUID,
    db: Session = Depends(get_db),
) -> ProfileEnvelope:
    return get_public_profile(db, user_id)
