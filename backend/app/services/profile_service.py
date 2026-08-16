from pathlib import Path
from typing import Dict, Set
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.profile import (
    EmployerProfile,
    MentorProfile,
    StudentProfile,
)
from app.models.user import User, UserRole
from app.repositories.profile_repository import (
    create_profile_for_user,
    get_profile_for_user,
    update_profile_fields,
)
from app.repositories.user_repository import get_user_by_id
from app.schemas.auth_schema import UserResponse
from app.schemas.profile_schema import (
    EmployerProfileResponse,
    MentorProfileResponse,
    ProfileEnvelope,
    ProfileUpdateRequest,
    StudentProfileResponse,
)


STUDENT_FIELDS: Set[str] = {
    "first_name",
    "last_name",
    "headline",
    "summary",
    "education",
    "work_experience",
    "preferred_roles",
    "preferred_locations",
    "work_authorization",
    "availability",
    "career_goals",
    "github_url",
    "linkedin_url",
    "portfolio_url",
    "is_public",
}

EMPLOYER_FIELDS: Set[str] = {
    "company_name",
    "industry",
    "company_size",
    "website",
    "description",
    "location",
    "is_public",
}

MENTOR_FIELDS: Set[str] = {
    "display_name",
    "headline",
    "bio",
    "industry",
    "years_of_experience",
    "languages",
    "mentorship_formats",
    "availability",
    "is_accepting_requests",
    "is_public",
}

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_RESUME_CONTENT_TYPES = {
    "application/pdf",
    (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    ),
}


def build_profile_envelope(
    user: User,
    profile,
) -> ProfileEnvelope:
    if isinstance(profile, StudentProfile):
        response = StudentProfileResponse.model_validate(profile)
    elif isinstance(profile, EmployerProfile):
        response = EmployerProfileResponse.model_validate(profile)
    elif isinstance(profile, MentorProfile):
        response = MentorProfileResponse.model_validate(profile)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile type is not supported",
        )

    return ProfileEnvelope(
        user=UserResponse.model_validate(user),
        profile_type=user.role,
        profile=response,
    )


def allowed_fields_for_role(role: UserRole) -> Set[str]:
    if role == UserRole.STUDENT:
        return STUDENT_FIELDS

    if role == UserRole.EMPLOYER:
        return EMPLOYER_FIELDS

    if role == UserRole.MENTOR:
        return MENTOR_FIELDS

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This role does not support a profile",
    )


def get_or_create_my_profile(
    db: Session,
    user: User,
) -> ProfileEnvelope:
    profile = get_profile_for_user(db, user)

    if profile is None:
        try:
            profile = create_profile_for_user(db, user)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        db.commit()
        db.refresh(profile)

    return build_profile_envelope(user, profile)


def update_my_profile(
    db: Session,
    user: User,
    request: ProfileUpdateRequest,
) -> ProfileEnvelope:
    submitted: Dict = request.model_dump(exclude_unset=True)

    if not submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile fields were provided",
        )

    allowed = allowed_fields_for_role(user.role)
    invalid_fields = set(submitted.keys()) - allowed

    if invalid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "These fields do not belong to your role: "
                + ", ".join(sorted(invalid_fields))
            ),
        )

    profile = get_profile_for_user(db, user)

    if profile is None:
        try:
            profile = create_profile_for_user(db, user)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    update_profile_fields(profile, submitted)

    db.commit()
    db.refresh(profile)

    return build_profile_envelope(user, profile)


def get_public_profile(
    db: Session,
    user_id: UUID,
) -> ProfileEnvelope:
    user = get_user_by_id(db, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    profile = get_profile_for_user(db, user)

    if profile is None or not profile.is_public:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return build_profile_envelope(user, profile)


async def upload_student_resume(
    db: Session,
    user: User,
    upload: UploadFile,
) -> ProfileEnvelope:
    if user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can upload resumes",
        )

    file_bytes = await upload.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file",
        )

    from app.services.storage_service import replace_student_resume

    replace_student_resume(
        db=db,
        user=user,
        file_bytes=file_bytes,
        file_name=upload.filename or "resume.pdf",
        content_type=upload.content_type or "application/pdf",
    )

    profile = get_profile_for_user(db, user)
    return build_profile_envelope(user, profile)
