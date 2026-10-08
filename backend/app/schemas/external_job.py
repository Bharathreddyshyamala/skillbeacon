from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ExternalJobResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    company_name: str
    title: str

    description: Optional[str]

    location: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]

    employment_type: Optional[str]
    workplace_type: Optional[str]
    department: Optional[str]

    job_url: str
    apply_url: Optional[str]

    posted_at: Optional[datetime]
    source_rank: Optional[int]

    created_at: datetime


class ExternalJobListResponse(
    BaseModel
):
    total: int
    page: int
    page_size: int

    items: list[
        ExternalJobResponse
    ]
