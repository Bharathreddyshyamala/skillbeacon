import enum

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
)

from app.models.mentorship import (
    MentorshipSessionStatus,
    MentorshipStatus,
)




class MentorshipDecision(str, enum.Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class SessionStatusUpdate(str, enum.Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"




class MentorSkillResponse(BaseModel):
    id: UUID
    name: str
    level: str
    confidence_score: int


class MentorDirectoryItem(BaseModel):
    mentor_id: UUID
    email: str
    name: str

    headline: Optional[str] = None
    bio: Optional[str] = None
    expertise: Optional[str] = None
    years_experience: Optional[int] = None

    skills: List[
        MentorSkillResponse
    ] = Field(
        default_factory=list
    )


class MentorDirectoryListResponse(BaseModel):
    items: List[
        MentorDirectoryItem
    ]

    total: int
    limit: int
    offset: int




class MentorshipCreateRequest(BaseModel):
    mentor_id: UUID

    focus_area: str = Field(
        min_length=2,
        max_length=200,
    )

    goals: str = Field(
        min_length=10,
        max_length=3000,
    )

    message: Optional[str] = Field(
        default=None,
        max_length=2000,
    )




class MentorshipRespondRequest(BaseModel):
    decision: MentorshipDecision

    mentor_response: Optional[str] = Field(
        default=None,
        max_length=2000,
    )




class MentorshipSessionCreateRequest(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=200,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=3000,
    )

    scheduled_start: datetime
    scheduled_end: datetime

    meeting_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    shared_notes: Optional[str] = Field(
        default=None,
        max_length=3000,
    )


class MentorshipSessionStatusRequest(BaseModel):
    status: SessionStatusUpdate

    shared_notes: Optional[str] = Field(
        default=None,
        max_length=3000,
    )


class MentorshipSessionResponse(BaseModel):
    id: UUID
    mentorship_id: UUID
    created_by_id: UUID

    title: str
    description: Optional[str]

    scheduled_start: datetime
    scheduled_end: datetime

    meeting_url: Optional[str]
    shared_notes: Optional[str]

    status: MentorshipSessionStatus

    created_at: datetime
    updated_at: datetime




class MentorshipResponse(BaseModel):
    id: UUID

    student_id: UUID
    student_name: str
    student_email: str

    mentor_id: UUID
    mentor_name: str
    mentor_email: str

    focus_area: str
    goals: str

    message: Optional[str]
    mentor_response: Optional[str]

    status: MentorshipStatus

    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime

    sessions: List[
        MentorshipSessionResponse
    ] = Field(
        default_factory=list
    )


class MentorshipListResponse(BaseModel):
    items: List[
        MentorshipResponse
    ]

    total: int
    limit: int
    offset: int