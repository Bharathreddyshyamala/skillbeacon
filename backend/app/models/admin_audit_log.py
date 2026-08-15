import uuid

from datetime import datetime

from typing import (
    Any,
    Dict,
    Optional,
)

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
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


class AdminAuditLog(Base):
    """
    Records sensitive actions performed by administrators.

    Examples:

    deactivate_user
    activate_user
    verify_user
    unverify_user
    close_opportunity
    reopen_opportunity
    close_challenge
    reopen_challenge
    """

    __tablename__ = "admin_audit_logs"

    __table_args__ = (
        Index(
            "ix_admin_audit_logs_admin_id",
            "admin_id",
        ),
        Index(
            "ix_admin_audit_logs_action",
            "action",
        ),
        Index(
            "ix_admin_audit_logs_target_type",
            "target_type",
        ),
        Index(
            "ix_admin_audit_logs_created_at",
            "created_at",
        ),
    )


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


    admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    target_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    target_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )


    details: Mapped[
        Optional[Dict[str, Any]]
    ] = mapped_column(
        JSONB,
        nullable=True,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    admin = relationship(
        "User",
    )