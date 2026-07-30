from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.models.user import User


class StudentProfile(TimestampMixin, Base):
    __tablename__ = "student_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    headline: Mapped[Optional[str]] = mapped_column(String(200))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    education: Mapped[Optional[str]] = mapped_column(Text)
    work_experience: Mapped[Optional[str]] = mapped_column(Text)

    preferred_roles: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    preferred_locations: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    work_authorization: Mapped[Optional[str]] = mapped_column(String(100))
    availability: Mapped[Optional[str]] = mapped_column(String(100))
    career_goals: Mapped[Optional[str]] = mapped_column(Text)

    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))
    resume_path: Mapped[Optional[str]] = mapped_column(String(500))

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="student_profile",
    )


class EmployerProfile(TimestampMixin, Base):
    __tablename__ = "employer_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    company_name: Mapped[Optional[str]] = mapped_column(String(200))
    industry: Mapped[Optional[str]] = mapped_column(String(150))
    company_size: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(250))
    logo_path: Mapped[Optional[str]] = mapped_column(String(500))

    verification_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="employer_profile",
    )


class MentorProfile(TimestampMixin, Base):
    __tablename__ = "mentor_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    display_name: Mapped[Optional[str]] = mapped_column(String(200))
    headline: Mapped[Optional[str]] = mapped_column(String(200))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    industry: Mapped[Optional[str]] = mapped_column(String(150))
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer)

    languages: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    mentorship_formats: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    availability: Mapped[Optional[str]] = mapped_column(Text)

    is_accepting_requests: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="mentor_profile",
    )
