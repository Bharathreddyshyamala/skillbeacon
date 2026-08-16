from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum as SQLAlchemyEnum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.models.user import User


class DocumentType(str, enum.Enum):
    RESUME = "resume"
    SKILL_EVIDENCE = "skill_evidence"
    EMPLOYER_LOGO = "employer_logo"
    CHALLENGE_SUBMISSION = "challenge_submission"
    GENERAL = "general"


class Document(TimestampMixin, Base):
    """
    Centralized registry for user-uploaded documents and media stored in Cloudflare R2 / S3.
    """

    __tablename__ = "documents"

    __table_args__ = (
        Index("ix_documents_user_id", "user_id"),
        Index("ix_documents_document_type", "document_type"),
        Index("ix_documents_user_type", "user_id", "document_type"),
        Index("ix_documents_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        SQLAlchemyEnum(
            DocumentType,
            name="document_type",
            values_callable=lambda enum_class: [
                doc_type.value for doc_type in enum_class
            ],
        ),
        nullable=False,
        default=DocumentType.GENERAL,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="documents",
    )
