from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import (
    EmployerProfile,
    MentorProfile,
    StudentProfile,
)
from app.models.user import User, UserRole


ProfileModel = Union[
    StudentProfile,
    EmployerProfile,
    MentorProfile,
]


def get_student_profile(
    db: Session,
    user_id: UUID,
) -> Optional[StudentProfile]:
    statement = select(StudentProfile).where(
        StudentProfile.user_id == user_id
    )
    return db.scalar(statement)


def get_employer_profile(
    db: Session,
    user_id: UUID,
) -> Optional[EmployerProfile]:
    statement = select(EmployerProfile).where(
        EmployerProfile.user_id == user_id
    )
    return db.scalar(statement)


def get_mentor_profile(
    db: Session,
    user_id: UUID,
) -> Optional[MentorProfile]:
    statement = select(MentorProfile).where(
        MentorProfile.user_id == user_id
    )
    return db.scalar(statement)


def get_profile_for_user(
    db: Session,
    user: User,
) -> Optional[ProfileModel]:
    if user.role == UserRole.STUDENT:
        return get_student_profile(db, user.id)

    if user.role == UserRole.EMPLOYER:
        return get_employer_profile(db, user.id)

    if user.role == UserRole.MENTOR:
        return get_mentor_profile(db, user.id)

    return None


def create_profile_for_user(
    db: Session,
    user: User,
) -> ProfileModel:
    if user.role == UserRole.STUDENT:
        profile: ProfileModel = StudentProfile(user_id=user.id)
    elif user.role == UserRole.EMPLOYER:
        profile = EmployerProfile(user_id=user.id)
    elif user.role == UserRole.MENTOR:
        profile = MentorProfile(user_id=user.id)
    else:
        raise ValueError(
            "This user role does not have a profile type"
        )

    db.add(profile)
    db.flush()
    return profile


def update_profile_fields(
    profile: ProfileModel,
    values: dict,
) -> ProfileModel:
    for field_name, value in values.items():
        setattr(profile, field_name, value)

    return profile
