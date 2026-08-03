from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.skill import (
    Skill,
    SkillEvidence,
    SkillVerification,
    UserSkill,
    VerificationStatus,
)
from app.models.user import User


def list_active_skills(
    db: Session,
) -> List[Skill]:
    statement = (
        select(Skill)
        .where(Skill.is_active.is_(True))
        .order_by(
            Skill.category.asc(),
            Skill.name.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_skill_by_id(
    db: Session,
    skill_id: UUID,
) -> Optional[Skill]:
    return db.get(Skill, skill_id)


def get_skill_by_name(
    db: Session,
    name: str,
) -> Optional[Skill]:
    statement = select(Skill).where(
        Skill.name.ilike(name.strip())
    )

    return db.scalar(statement)


def create_skill(
    db: Session,
    *,
    name: str,
    category: Optional[str],
    description: Optional[str],
) -> Skill:
    skill = Skill(
        name=name.strip(),
        category=category.strip()
        if category
        else None,
        description=description,
    )

    db.add(skill)
    db.flush()

    return skill


def get_user_skill(
    db: Session,
    user_skill_id: UUID,
) -> Optional[UserSkill]:
    statement = (
        select(UserSkill)
        .where(
            UserSkill.id == user_skill_id
        )
        .options(
            selectinload(UserSkill.skill),
            selectinload(UserSkill.evidence)
            .selectinload(
                SkillEvidence.verifications
            ),
        )
    )

    return db.scalar(statement)


def get_user_skill_by_skill(
    db: Session,
    user_id: UUID,
    skill_id: UUID,
) -> Optional[UserSkill]:
    statement = select(UserSkill).where(
        UserSkill.user_id == user_id,
        UserSkill.skill_id == skill_id,
    )

    return db.scalar(statement)


def list_user_skills(
    db: Session,
    user_id: UUID,
) -> List[UserSkill]:
    statement = (
        select(UserSkill)
        .where(
            UserSkill.user_id == user_id
        )
        .options(
            selectinload(UserSkill.skill),
            selectinload(UserSkill.evidence)
            .selectinload(
                SkillEvidence.verifications
            ),
        )
        .order_by(UserSkill.created_at.desc())
    )

    return list(
        db.scalars(statement)
        .unique()
        .all()
    )


def create_user_skill(
    db: Session,
    *,
    user_id: UUID,
    skill_id: UUID,
    level,
    confidence_score: float,
) -> UserSkill:
    user_skill = UserSkill(
        user_id=user_id,
        skill_id=skill_id,
        level=level,
        confidence_score=confidence_score,
    )

    db.add(user_skill)
    db.flush()

    return user_skill


def delete_user_skill(
    db: Session,
    user_skill: UserSkill,
) -> None:
    db.delete(user_skill)


def create_evidence(
    db: Session,
    *,
    user_skill_id: UUID,
    evidence_type,
    title: str,
    description: Optional[str],
    url: Optional[str],
    score: Optional[float],
) -> SkillEvidence:
    evidence = SkillEvidence(
        user_skill_id=user_skill_id,
        evidence_type=evidence_type,
        title=title,
        description=description,
        url=url,
        score=score,
    )

    db.add(evidence)
    db.flush()

    return evidence


def get_evidence(
    db: Session,
    evidence_id: UUID,
) -> Optional[SkillEvidence]:
    statement = (
        select(SkillEvidence)
        .where(
            SkillEvidence.id == evidence_id
        )
        .options(
            selectinload(
                SkillEvidence.user_skill
            ),
            selectinload(
                SkillEvidence.verifications
            ),
        )
    )

    return db.scalar(statement)


def get_verification(
    db: Session,
    evidence_id: UUID,
    verifier_id: UUID,
) -> Optional[SkillVerification]:
    statement = select(
        SkillVerification
    ).where(
        SkillVerification.evidence_id
        == evidence_id,
        SkillVerification.verifier_id
        == verifier_id,
    )

    return db.scalar(statement)


def create_verification(
    db: Session,
    *,
    evidence_id: UUID,
    verifier_id: UUID,
    status,
    comments: Optional[str],
) -> SkillVerification:
    verification = SkillVerification(
        evidence_id=evidence_id,
        verifier_id=verifier_id,
        status=status,
        comments=comments,
    )

    db.add(verification)
    db.flush()

    return verification

def list_pending_evidence(
    db: Session,
):
    statement = (
        select(
            SkillEvidence,
            UserSkill,
            Skill,
            User,
        )
        .join(
            UserSkill,
            SkillEvidence.user_skill_id
            == UserSkill.id,
        )
        .join(
            Skill,
            UserSkill.skill_id
            == Skill.id,
        )
        .join(
            User,
            UserSkill.user_id
            == User.id,
        )
        .where(
            SkillEvidence.status
            == VerificationStatus.PENDING
        )
        .order_by(
            SkillEvidence.created_at.asc()
        )
    )

    return db.execute(statement).all()