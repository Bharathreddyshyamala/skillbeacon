import uuid

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    String,
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
)

from app.models.base import Base


class SampleDataBatch(Base):
    __tablename__ = "sample_data_batches"

    __table_args__ = (
        Index(
            "ix_sample_data_batches_status",
            "status",
        ),
        Index(
            "ix_sample_data_batches_created_at",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    uploaded_by_admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    source_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="importing",
    )

    row_counts: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    validation_errors: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )

    storage_cleanup_errors: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class SampleDataRecord(Base):
    __tablename__ = "sample_data_records"

    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "table_name",
            "logical_key",
            name="uq_sample_data_record_key",
        ),
        Index(
            "ix_sample_data_records_batch_id",
            "batch_id",
        ),
        Index(
            "ix_sample_data_records_table_name",
            "table_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sample_data_batches.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    table_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    logical_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    pk_values: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class SampleDataObject(Base):
    __tablename__ = "sample_data_objects"

    __table_args__ = (
        UniqueConstraint(
            "batch_id",
            "object_key",
            name="uq_sample_data_object_key",
        ),
        Index(
            "ix_sample_data_objects_batch_id",
            "batch_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sample_data_batches.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    bucket_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    object_key: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    content_type: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )