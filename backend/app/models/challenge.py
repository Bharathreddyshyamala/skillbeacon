import enum
import uuid

from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base







class ChallengeType(str, enum.Enum):
    CODING = "coding"
    DATA = "data"
    CASE_STUDY = "case_study"
    DESIGN = "design"
    GENERAL = "general"


class ChallengeDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ChallengeStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


class ChallengeSkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ChallengeSubmissionStatus(
    str,
    enum.Enum,
):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"







class Challenge(Base):
    __tablename__ = "challenges"

    __table_args__ = (
        Index(
            "ix_challenges_employer_id",
            "employer_id",
        ),
        Index(
            "ix_challenges_status",
            "status",
        ),
        Index(
            "ix_challenges_type",
            "challenge_type",
        ),
        Index(
            "ix_challenges_deadline",
            "deadline",
        ),
        Index(
            "ix_challenges_created_at",
            "created_at",
        ),
    )


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )


    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    instructions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


    deliverables: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


    challenge_type: Mapped[
        ChallengeType
    ] = mapped_column(
        SAEnum(
            ChallengeType,
            name="challenge_type",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
    )


    difficulty: Mapped[
        ChallengeDifficulty
    ] = mapped_column(
        SAEnum(
            ChallengeDifficulty,
            name="challenge_difficulty",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
    )


    status: Mapped[
        ChallengeStatus
    ] = mapped_column(
        SAEnum(
            ChallengeStatus,
            name="challenge_status",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
        default=ChallengeStatus.DRAFT,
    )


    deadline: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


    employer = relationship(
        "User",
        back_populates="employer_challenges",
    )


    skills: Mapped[
        List["ChallengeSkill"]
    ] = relationship(
        "ChallengeSkill",
        back_populates="challenge",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


    submissions: Mapped[
        List["ChallengeSubmission"]
    ] = relationship(
        "ChallengeSubmission",
        back_populates="challenge",
        lazy="selectin",
    )







class ChallengeSkill(Base):
    __tablename__ = "challenge_skills"

    __table_args__ = (
        UniqueConstraint(
            "challenge_id",
            "skill_id",
            name=(
                "uq_challenge_skill_"
                "challenge_skill"
            ),
        ),
    )


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "challenges.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "skills.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


    minimum_level: Mapped[
        ChallengeSkillLevel
    ] = mapped_column(
        SAEnum(
            ChallengeSkillLevel,
            name="challenge_skill_level",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
    )


    required: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )


    challenge = relationship(
        "Challenge",
        back_populates="skills",
    )


    skill = relationship(
        "Skill",
    )







class ChallengeSubmission(Base):
    __tablename__ = "challenge_submissions"

    __table_args__ = (
        UniqueConstraint(
            "challenge_id",
            "student_id",
            name=(
                "uq_challenge_submission_"
                "challenge_student"
            ),
        ),

        CheckConstraint(
            "score IS NULL OR "
            "(score >= 0 AND score <= 100)",
            name=(
                "ck_challenge_submission_score"
            ),
        ),

        Index(
            "ix_challenge_submissions_challenge_id",
            "challenge_id",
        ),

        Index(
            "ix_challenge_submissions_student_id",
            "student_id",
        ),

        Index(
            "ix_challenge_submissions_status",
            "status",
        ),

        Index(
            "ix_challenge_submissions_created_at",
            "created_at",
        ),
    )


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    challenge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "challenges.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


    submission_text: Mapped[
        Optional[str]
    ] = mapped_column(
        Text,
        nullable=True,
    )


    repository_url: Mapped[
        Optional[str]
    ] = mapped_column(
        String(500),
        nullable=True,
    )


    demo_url: Mapped[
        Optional[str]
    ] = mapped_column(
        String(500),
        nullable=True,
    )


    profile_snapshot: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
    )


    status: Mapped[
        ChallengeSubmissionStatus
    ] = mapped_column(
        SAEnum(
            ChallengeSubmissionStatus,
            name=(
                "challenge_submission_status"
            ),
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
        default=(
            ChallengeSubmissionStatus.SUBMITTED
        ),
    )


    score: Mapped[
        Optional[int]
    ] = mapped_column(
        Integer,
        nullable=True,
    )


    employer_feedback: Mapped[
        Optional[str]
    ] = mapped_column(
        Text,
        nullable=True,
    )


    reviewed_at: Mapped[
        Optional[datetime]
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


    challenge = relationship(
        "Challenge",
        back_populates="submissions",
    )


    student = relationship(
        "User",
        back_populates=(
            "challenge_submissions"
        ),
    )