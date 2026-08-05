from typing import Dict
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.skill import (
    SkillLevel,
    VerificationStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.skill_repository import (
    create_evidence,
    create_skill,
    create_user_skill,
    create_verification,
    delete_user_skill,
    get_evidence,
    get_skill_by_id,
    get_skill_by_name,
    get_user_skill,
    get_user_skill_by_skill,
    get_verification,
    list_active_skills,
    list_user_skills,
    list_pending_evidence,
)

from app.schemas.skill_schema import (
    EvidenceCreateRequest,
    SkillCreateRequest,
    UserSkillCreateRequest,
    UserSkillUpdateRequest,
    VerificationCreateRequest,
)



LEVEL_SCORES: Dict[SkillLevel, float] = {
    SkillLevel.BEGINNER: 20.0,
    SkillLevel.INTERMEDIATE: 40.0,
    SkillLevel.ADVANCED: 60.0,
    SkillLevel.EXPERT: 75.0,
}



def calculate_confidence_score(
    user_skill,
) -> float:
    """
    Calculate the confidence score for a user's skill.

    Base score comes from the user's selected skill level.

    Additional points:
    - Approved evidence gives bonus points.
    - Approved mentor/employer/admin verification
      gives additional bonus points.

    Maximum score = 100.
    """

    score = LEVEL_SCORES.get(
        user_skill.level,
        0.0,
    )

    approved_evidence_count = 0
    mentor_or_employer_approvals = 0

    for evidence in user_skill.evidence:

        if (
            evidence.status
            == VerificationStatus.APPROVED
        ):
            approved_evidence_count += 1

        for verification in evidence.verifications:

            if (
                verification.status
                == VerificationStatus.APPROVED
            ):
                mentor_or_employer_approvals += 1


    if approved_evidence_count > 0:
        score += 10


    if approved_evidence_count > 1:

        score += min(
            (approved_evidence_count - 1) * 5,
            10,
        )


    score += min(
        mentor_or_employer_approvals * 10,
        20,
    )


    return min(
        score,
        100.0,
    )



def ensure_skill_owner_role(
    user: User,
) -> None:
    """
    Students and mentors can maintain
    their own Skill Passport.
    """

    allowed_roles = {
        UserRole.STUDENT,
        UserRole.MENTOR,
    }

    if user.role not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This role cannot manage a personal "
                "Skill Passport."
            ),
        )



def list_skill_catalog(
    db: Session,
):
    """
    Return all active skills available
    in the SkillBeacon skill catalog.
    """

    return list_active_skills(db)



def create_catalog_skill(
    db: Session,
    current_user: User,
    request: SkillCreateRequest,
):
    """
    Only administrators can create
    skills in the global skill catalog.
    """

    if current_user.role != UserRole.ADMIN:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only administrators can create skills."
            ),
        )


    existing = get_skill_by_name(
        db,
        request.name,
    )


    if existing:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill already exists.",
        )


    skill = create_skill(
        db,
        name=request.name,
        category=request.category,
        description=request.description,
    )


    db.commit()
    db.refresh(skill)


    return skill



def get_my_skills(
    db: Session,
    current_user: User,
):
    """
    Return the logged-in user's
    complete Skill Passport.
    """

    ensure_skill_owner_role(
        current_user
    )


    return list_user_skills(
        db,
        current_user.id,
    )



def add_my_skill(
    db: Session,
    current_user: User,
    request: UserSkillCreateRequest,
):
    """
    Add a skill from the global catalog
    to the current user's Skill Passport.
    """

    ensure_skill_owner_role(
        current_user
    )


    skill = get_skill_by_id(
        db,
        request.skill_id,
    )


    if not skill or not skill.is_active:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )


    existing = get_user_skill_by_skill(
        db,
        current_user.id,
        request.skill_id,
    )


    if existing:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "You already added this skill."
            ),
        )


    user_skill = create_user_skill(
        db,
        user_id=current_user.id,
        skill_id=skill.id,
        level=request.level,
        confidence_score=LEVEL_SCORES[
            request.level
        ],
    )


    db.commit()


    return get_user_skill(
        db,
        user_skill.id,
    )



def update_my_skill(
    db: Session,
    current_user: User,
    user_skill_id: UUID,
    request: UserSkillUpdateRequest,
):
    """
    Update the user's skill level and
    recalculate the confidence score.
    """

    ensure_skill_owner_role(
        current_user
    )


    user_skill = get_user_skill(
        db,
        user_skill_id,
    )


    if not user_skill:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found.",
        )


    if user_skill.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot update this skill."
            ),
        )


    user_skill.level = request.level


    user_skill.confidence_score = (
        calculate_confidence_score(
            user_skill
        )
    )


    db.commit()


    return get_user_skill(
        db,
        user_skill.id,
    )



def remove_my_skill(
    db: Session,
    current_user: User,
    user_skill_id: UUID,
) -> None:
    """
    Remove a skill from the current
    user's Skill Passport.
    """

    ensure_skill_owner_role(
        current_user
    )


    user_skill = get_user_skill(
        db,
        user_skill_id,
    )


    if not user_skill:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found.",
        )


    if user_skill.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot delete this skill."
            ),
        )


    delete_user_skill(
        db,
        user_skill,
    )


    db.commit()



def add_skill_evidence(
    db: Session,
    current_user: User,
    user_skill_id: UUID,
    request: EvidenceCreateRequest,
):
    """
    Add evidence to one of the current
    user's skills.

    Examples:
    - GitHub project
    - Certificate
    - Assessment
    - Work experience
    - Employer challenge
    """

    ensure_skill_owner_role(
        current_user
    )


    user_skill = get_user_skill(
        db,
        user_skill_id,
    )


    if not user_skill:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found.",
        )


    if user_skill.user_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot add evidence "
                "to another user's skill."
            ),
        )


    create_evidence(
        db,
        user_skill_id=user_skill.id,
        evidence_type=request.evidence_type,
        title=request.title,
        description=request.description,
        url=request.url,
        score=request.score,
    )


    db.commit()


    return get_user_skill(
        db,
        user_skill.id,
    )



def verify_evidence(
    db: Session,
    current_user: User,
    evidence_id: UUID,
    request: VerificationCreateRequest,
):
    """
    Mentor, employer, or admin reviews
    submitted skill evidence.

    Evidence can become:

    - APPROVED
    - REJECTED
    - PENDING

    The user's confidence score is
    recalculated after verification.
    """


    allowed_roles = {
        UserRole.MENTOR,
        UserRole.EMPLOYER,
        UserRole.ADMIN,
    }


    if current_user.role not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only mentors, employers, or admins "
                "can verify evidence."
            ),
        )



    evidence = get_evidence(
        db,
        evidence_id,
    )


    if not evidence:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found.",
        )



    if (
        evidence.user_skill.user_id
        == current_user.id
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot verify your own evidence."
            ),
        )



    existing = get_verification(
        db,
        evidence.id,
        current_user.id,
    )


    if existing:


        existing.status = (
            request.status
        )

        existing.comments = (
            request.comments
        )

    else:


        create_verification(
            db,
            evidence_id=evidence.id,
            verifier_id=current_user.id,
            status=request.status,
            comments=request.comments,
        )


    db.flush()



    db.expire_all()


    evidence = get_evidence(
        db,
        evidence_id,
    )


    if not evidence:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found.",
        )



    verification_statuses = [

        verification.status

        for verification
        in evidence.verifications

    ]



    if (
        VerificationStatus.APPROVED
        in verification_statuses
    ):

        evidence.status = (
            VerificationStatus.APPROVED
        )



    elif (
        VerificationStatus.REJECTED
        in verification_statuses
    ):

        evidence.status = (
            VerificationStatus.REJECTED
        )



    else:

        evidence.status = (
            VerificationStatus.PENDING
        )


    db.flush()



    db.expire_all()


    user_skill = get_user_skill(
        db,
        evidence.user_skill_id,
    )


    if not user_skill:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found.",
        )



    user_skill.confidence_score = (
        calculate_confidence_score(
            user_skill
        )
    )



    db.commit()


    return get_user_skill(
        db,
        user_skill.id,
    )



def get_pending_evidence(
    db: Session,
    current_user: User,
):
    """
    Return evidence waiting for verification.

    Available only to:
    - Mentor
    - Employer
    - Admin

    Users cannot review their own evidence.
    """

    allowed_roles = {
        UserRole.MENTOR,
        UserRole.EMPLOYER,
        UserRole.ADMIN,
    }


    if current_user.role not in allowed_roles:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only mentors, employers, or admins "
                "can review evidence."
            ),
        )


    rows = list_pending_evidence(
        db
    )


    results = []


    for (
        evidence,
        user_skill,
        skill,
        owner,
    ) in rows:



        if owner.id == current_user.id:
            continue


        results.append(
            {
                "id":
                    evidence.id,

                "user_skill_id":
                    user_skill.id,

                "owner_id":
                    owner.id,

                "owner_email":
                    owner.email,

                "skill_name":
                    skill.name,

                "level":
                    user_skill.level,

                "evidence_type":
                    evidence.evidence_type,

                "title":
                    evidence.title,

                "description":
                    evidence.description,

                "url":
                    evidence.url,

                "score":
                    evidence.score,

                "status":
                    evidence.status,

                "created_at":
                    evidence.created_at,
            }
        )


    return results