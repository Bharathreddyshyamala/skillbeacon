from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.models.base import Base


class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_name = Column(
        String(255),
        nullable=False,
        index=True,
    )

    careers_url = Column(
        Text,
        nullable=False,
    )

    # amazon | microsoft | greenhouse | lever
    connector_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    # Microsoft -> microsoft.com
    # Greenhouse -> board token
    # Lever -> site slug
    # Amazon -> usually None
    connector_key = Column(
        String(255),
        nullable=True,
    )

    config_json = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    last_synced_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_sync_status = Column(
        String(30),
        nullable=True,
    )

    last_sync_error = Column(
        Text,
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