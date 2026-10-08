from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.models.base import Base


class ExternalJob(Base):
    __tablename__ = "external_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_id = Column(
        Integer,
        ForeignKey(
            "job_sources.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    company_name = Column(
        String(255),
        nullable=False,
        index=True,
    )

    external_job_id = Column(
        String(255),
        nullable=False,
    )

    title = Column(
        String(500),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    location = Column(
        String(500),
        nullable=True,
        index=True,
    )

    city = Column(
        String(255),
        nullable=True,
    )

    state = Column(
        String(255),
        nullable=True,
    )

    country = Column(
        String(100),
        nullable=True,
        index=True,
    )

    employment_type = Column(
        String(100),
        nullable=True,
    )

    workplace_type = Column(
        String(100),
        nullable=True,
    )

    department = Column(
        String(255),
        nullable=True,
    )

    job_url = Column(
        Text,
        nullable=False,
    )

    apply_url = Column(
        Text,
        nullable=True,
    )

    posted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    source_updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    source_rank = Column(
        Integer,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    first_seen_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    last_seen_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Useful while developing connectors.
    raw_payload = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "external_job_id",
            name="uq_external_job_source_external_id",
        ),
        Index(
            "ix_external_jobs_active_company",
            "is_active",
            "company_name",
        ),
        Index(
            "ix_external_jobs_source_rank",
            "source_id",
            "source_rank",
        ),
    )
