import enum
import uuid

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
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


class MentorshipStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class MentorshipSessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============================================================
# Mentorship
# ============================================================


class Mentorship(Base):
    __tablename__ = "mentorships"

    __table_args__ = (
        Index(
            "ix_mentorships_student_id",
            "student_id",
        ),
        Index(
            "ix_mentorships_mentor_id",
            "mentor_id",
        ),
        Index(
            "ix_mentorships_status",
            "status",
        ),
        Index(
            "ix_mentorships_created_at",
            "created_at",
        ),

        # A student cannot have multiple
        # pending/active mentorships with
        # the same mentor.
        #
        # Rejected/cancelled/completed records
        # remain as history and do not block
        # a future request.
        Index(
            "uq_active_mentorship_pair",
            "student_id",
            "mentor_id",
            unique=True,
            postgresql_where=text(
                "status IN ('pending', 'active')"
            ),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    focus_area: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    goals: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    mentor_response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[MentorshipStatus] = mapped_column(
        SAEnum(
            MentorshipStatus,
            name="mentorship_status",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
        default=MentorshipStatus.PENDING,
    )

    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
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

    student = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="student_mentorships",
    )

    mentor = relationship(
        "User",
        foreign_keys=[mentor_id],
        back_populates="mentor_mentorships",
    )

    sessions: Mapped[List["MentorshipSession"]] = relationship(
        "MentorshipSession",
        back_populates="mentorship",
        cascade="all, delete-orphan",
        order_by="MentorshipSession.scheduled_start",
        lazy="selectin",
    )


# ============================================================
# Mentorship Session
# ============================================================


class MentorshipSession(Base):
    __tablename__ = "mentorship_sessions"

    __table_args__ = (
        Index(
            "ix_mentorship_sessions_mentorship_id",
            "mentorship_id",
        ),
        Index(
            "ix_mentorship_sessions_status",
            "status",
        ),
        Index(
            "ix_mentorship_sessions_scheduled_start",
            "scheduled_start",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    mentorship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "mentorships.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    created_by_id: Mapped[uuid.UUID] = mapped_column(
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

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    meeting_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    shared_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[
        MentorshipSessionStatus
    ] = mapped_column(
        SAEnum(
            MentorshipSessionStatus,
            name="mentorship_session_status",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
        default=(
            MentorshipSessionStatus.SCHEDULED
        ),
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

    mentorship = relationship(
        "Mentorship",
        back_populates="sessions",
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
    )