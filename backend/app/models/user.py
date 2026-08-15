from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum as SQLAlchemyEnum, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.models.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.models.profile import (
        EmployerProfile,
        MentorProfile,
        StudentProfile,
    )
    from app.models.refresh_token import RefreshToken
    from app.models.skill import UserSkill
    from app.models.application import Application


class UserRole(str, enum.Enum):
    STUDENT = "student"
    EMPLOYER = "employer"
    MENTOR = "mentor"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(TimestampMixin, Base):
    """
    Main user account table.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_class: [
                role.value for role in enum_class
            ],
        ),
        nullable=False,
        default=UserRole.STUDENT,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
    "StudentProfile",
    back_populates="user",
    cascade="all, delete-orphan",
    passive_deletes=True,
    uselist=False,
    )

    employer_profile: Mapped[Optional["EmployerProfile"]] = relationship(
        "EmployerProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )

    mentor_profile: Mapped[Optional["MentorProfile"]] = relationship(
        "MentorProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    skills: Mapped[List["UserSkill"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
    passive_deletes=True,
    )

    applications: Mapped[List["Application"]] = relationship(
        "Application",
        back_populates="student",
        foreign_keys="Application.student_id",
    )
    student_mentorships = relationship(
    "Mentorship",
    foreign_keys="Mentorship.student_id",
    back_populates="student",
    )

    mentor_mentorships = relationship(
        "Mentorship",
        foreign_keys="Mentorship.mentor_id",
        back_populates="mentor",
    )
    employer_challenges = relationship(
    "Challenge",
    back_populates="employer",
    )
    challenge_submissions = relationship(
    "ChallengeSubmission",
    back_populates="student",
    )
    notifications = relationship(
    "Notification",
    back_populates="user",
    cascade="all, delete-orphan",
    )