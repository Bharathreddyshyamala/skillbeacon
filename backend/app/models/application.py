import enum
import uuid

from typing import Dict, Optional

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
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

from app.models.base import Base, TimestampMixin


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "opportunity_id",
            "student_id",
            name=(
                "uq_application_"
                "opportunity_student"
            ),
        ),

        Index(
            "ix_applications_opportunity_id",
            "opportunity_id",
        ),

        Index(
            "ix_applications_student_id",
            "student_id",
        ),

        Index(
            "ix_applications_status",
            "status",
        ),

        Index(
            "ix_applications_created_at",
            "created_at",
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

    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(
            ApplicationStatus,
            name="application_status",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ],
        ),
        nullable=False,
        default=ApplicationStatus.SUBMITTED,
    )

    cover_letter: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Stored internally only.
    # Never return this raw path to frontend.
    resume_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Historical copy of student's profile
    # at application submission time.
    profile_snapshot: Mapped[Dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Private employer-only note.
    employer_note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    student = relationship(
        "User",
        back_populates="applications",
        foreign_keys=[student_id],
    )

    opportunity = relationship(
        "Opportunity",
        back_populates="applications",
    )