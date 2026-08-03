import enum
import uuid

from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base, TimestampMixin


# ============================================================
# Enums
# ============================================================


class OpportunityType(str, enum.Enum):
    JOB = "job"
    INTERNSHIP = "internship"
    PROJECT = "project"
    VOLUNTEER = "volunteer"


class WorkMode(str, enum.Enum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"


class OpportunityStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


# ============================================================
# Opportunity
# ============================================================


class Opportunity(Base):

    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    employer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
    )

    work_mode: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=WorkMode.ONSITE.value,
    )

    opportunity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=OpportunityType.JOB.value,
    )

    employment_type: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )

    salary_min = mapped_column(
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=True,
    )

    salary_max = mapped_column(
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    application_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    deadline = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=OpportunityStatus.DRAFT.value,
        index=True,
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    employer = relationship(
        "User",
    )

    skills = relationship(
        "OpportunitySkill",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    applications = relationship(
    "Application",
    back_populates="opportunity",
    passive_deletes=True,
    )


# ============================================================
# Opportunity Skill Requirement
# ============================================================


class OpportunitySkill(Base):

    __tablename__ = "opportunity_skills"

    __table_args__ = (
        UniqueConstraint(
            "opportunity_id",
            "skill_id",
            name="uq_opportunity_skill",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "opportunities.id",
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

    minimum_level: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="beginner",
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    opportunity = relationship(
        "Opportunity",
        back_populates="skills",
    )

    skill = relationship(
        "Skill",
        lazy="joined",
    )