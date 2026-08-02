import enum
import uuid
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.models.user import User


class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class EvidenceType(str, enum.Enum):
    GITHUB_PROJECT = "github_project"
    CERTIFICATE = "certificate"
    ASSESSMENT = "assessment"
    EMPLOYER_CHALLENGE = "employer_challenge"
    WORK_EXPERIENCE = "work_experience"
    MENTOR_REVIEW = "mentor_review"
    OTHER = "other"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Skill(TimestampMixin, Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(120),
        nullable=True,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    user_skills: Mapped[List["UserSkill"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserSkill(TimestampMixin, Base):
    __tablename__ = "user_skills"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "skill_id",
            name="uq_user_skill",
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 100",
            name="ck_user_skill_confidence_score",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    level: Mapped[SkillLevel] = mapped_column(
        Enum(
            SkillLevel,
            name="skill_level",
            values_callable=lambda obj: [
                item.value for item in obj
            ],
        ),
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    user: Mapped["User"] = relationship(
        back_populates="skills",
    )

    skill: Mapped["Skill"] = relationship(
        back_populates="user_skills",
    )

    evidence: Mapped[List["SkillEvidence"]] = relationship(
        back_populates="user_skill",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SkillEvidence(TimestampMixin, Base):
    __tablename__ = "skill_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(
            EvidenceType,
            name="evidence_type",
            values_callable=lambda obj: [
                item.value for item in obj
            ],
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="verification_status",
            values_callable=lambda obj: [
                item.value for item in obj
            ],
        ),
        nullable=False,
        default=VerificationStatus.PENDING,
    )

    user_skill: Mapped["UserSkill"] = relationship(
        back_populates="evidence",
    )

    verifications: Mapped[List["SkillVerification"]] = relationship(
        back_populates="evidence",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SkillVerification(TimestampMixin, Base):
    __tablename__ = "skill_verifications"

    __table_args__ = (
        UniqueConstraint(
            "evidence_id",
            "verifier_id",
            name="uq_evidence_verifier",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "skill_evidence.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    verifier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="skill_verification_status",
            values_callable=lambda obj: [
                item.value for item in obj
            ],
        ),
        nullable=False,
    )

    comments: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    evidence: Mapped["SkillEvidence"] = relationship(
        back_populates="verifications",
    )

    verifier: Mapped["User"] = relationship(
        foreign_keys=[verifier_id],
    )