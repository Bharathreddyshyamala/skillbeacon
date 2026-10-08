from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class NormalizedJob(BaseModel):
    external_job_id: str
    company_name: str

    title: str
    description: Optional[str] = None

    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    employment_type: Optional[str] = None
    workplace_type: Optional[str] = None
    department: Optional[str] = None

    job_url: str
    apply_url: Optional[str] = None

    posted_at: Optional[datetime] = None
    source_updated_at: Optional[datetime] = None
    source_rank: Optional[int] = None

    raw_payload: dict[str, Any] = Field(
        default_factory=dict
    )


class ConnectorFetchResult(BaseModel):
    jobs: list[NormalizedJob]

    # True means we believe we fetched the complete
    # current result set for this source.
    is_complete: bool = True

    # True means the fetched jobs are the complete
    # active window we want to expose, even if the
    # upstream source has more jobs outside that window.
    deactivate_unseen: bool = False
