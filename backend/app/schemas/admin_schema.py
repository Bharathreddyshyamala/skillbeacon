from datetime import (
    date,
    datetime,
)

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from uuid import UUID

from pydantic import BaseModel

from app.models.challenge import (
    ChallengeStatus,
)

from app.models.opportunity import (
    OpportunityStatus,
)


# ============================================================
# Dashboard
# ============================================================


class AdminDashboardResponse(BaseModel):

    total_users: int

    students: int

    mentors: int

    employers: int

    admins: int

    active_users: int

    inactive_users: int

    total_skills: int

    total_opportunities: int

    open_opportunities: int

    total_applications: int

    total_mentorships: int

    active_mentorships: int

    total_challenges: int

    open_challenges: int

    challenge_submissions: int


# ============================================================
# Users
# ============================================================


class AdminUserResponse(BaseModel):

    id: UUID

    email: str

    role: str

    is_active: bool

    is_verified: bool

    created_at: datetime

    updated_at: datetime


class AdminUserListResponse(BaseModel):

    items: List[
        AdminUserResponse
    ]

    total: int

    limit: int

    offset: int


class AdminUserStatusRequest(BaseModel):

    is_active: bool


class AdminUserVerificationRequest(BaseModel):

    is_verified: bool


# ============================================================
# Opportunities
# ============================================================


class AdminOpportunityResponse(BaseModel):

    id: UUID

    employer_id: UUID

    employer_email: str

    title: str

    company_name: str

    status: str

    deadline: Optional[date]

    created_at: datetime

    updated_at: datetime


class AdminOpportunityListResponse(BaseModel):

    items: List[
        AdminOpportunityResponse
    ]

    total: int

    limit: int

    offset: int


class AdminOpportunityStatusRequest(BaseModel):

    status: OpportunityStatus


# ============================================================
# Challenges
# ============================================================


class AdminChallengeResponse(BaseModel):

    id: UUID

    employer_id: UUID

    employer_email: str

    title: str

    company_name: str

    challenge_type: str

    difficulty: str

    status: str

    deadline: Optional[date]

    created_at: datetime

    updated_at: datetime


class AdminChallengeListResponse(BaseModel):

    items: List[
        AdminChallengeResponse
    ]

    total: int

    limit: int

    offset: int


class AdminChallengeStatusRequest(BaseModel):

    status: ChallengeStatus


# ============================================================
# Audit Log
# ============================================================


class AdminAuditLogResponse(BaseModel):

    id: UUID

    admin_id: UUID

    admin_email: str

    action: str

    target_type: str

    target_id: Optional[str]

    details: Optional[
        Dict[str, Any]
    ]

    created_at: datetime


class AdminAuditLogListResponse(BaseModel):

    items: List[
        AdminAuditLogResponse
    ]

    total: int

    limit: int

    offset: int