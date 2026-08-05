from datetime import datetime

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from app.models.application import (
    ApplicationStatus,
)




class ApplicationCreateRequest(BaseModel):

    opportunity_id: UUID

    cover_letter: Optional[str] = Field(
        default=None,
        max_length=5000,
    )




class ApplicationStatusRequest(BaseModel):

    status: ApplicationStatus

    employer_note: Optional[str] = Field(
        default=None,
        max_length=3000,
    )




class ApplicationNoteRequest(BaseModel):

    employer_note: Optional[str] = Field(
        default=None,
        max_length=3000,
    )




class StudentApplicationResponse(BaseModel):

    id: UUID

    opportunity_id: UUID

    opportunity_title: str

    company_name: str

    opportunity_type: str

    status: ApplicationStatus

    cover_letter: Optional[str]

    resume_available: bool

    created_at: datetime

    updated_at: datetime


class StudentApplicationListResponse(BaseModel):

    items: List[
        StudentApplicationResponse
    ]

    total: int

    limit: int

    offset: int




class EmployerApplicationResponse(BaseModel):

    id: UUID

    opportunity_id: UUID

    student_id: UUID

    student_email: str

    student_name: str

    status: ApplicationStatus

    cover_letter: Optional[str]

    profile_snapshot: Dict[
        str,
        Any,
    ]

    resume_available: bool

    employer_note: Optional[str]

    reviewed_at: Optional[datetime]

    created_at: datetime

    updated_at: datetime


class EmployerApplicationListResponse(BaseModel):

    items: List[
        EmployerApplicationResponse
    ]

    total: int

    limit: int

    offset: int