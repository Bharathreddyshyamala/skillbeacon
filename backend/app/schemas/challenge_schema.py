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

from pydantic import (
    BaseModel,
    Field,
)

from app.models.challenge import (
    ChallengeDifficulty,
    ChallengeSkillLevel,
    ChallengeStatus,
    ChallengeSubmissionStatus,
    ChallengeType,
)







class ChallengeSkillRequest(BaseModel):
    skill_id: UUID

    minimum_level: ChallengeSkillLevel

    required: bool = True


class ChallengeSkillResponse(BaseModel):
    id: UUID

    skill_id: UUID

    skill_name: str

    minimum_level: ChallengeSkillLevel

    required: bool







class ChallengeCreateRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    company_name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str = Field(
        min_length=10,
        max_length=10000,
    )

    instructions: str = Field(
        min_length=10,
        max_length=15000,
    )

    deliverables: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    challenge_type: ChallengeType

    difficulty: ChallengeDifficulty

    deadline: Optional[date] = None

    status: ChallengeStatus = (
        ChallengeStatus.DRAFT
    )

    skills: List[
        ChallengeSkillRequest
    ] = Field(
        default_factory=list
    )







class ChallengeUpdateRequest(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    company_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=10000,
    )

    instructions: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=15000,
    )

    deliverables: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    challenge_type: Optional[
        ChallengeType
    ] = None

    difficulty: Optional[
        ChallengeDifficulty
    ] = None

    deadline: Optional[date] = None

    skills: Optional[
        List[ChallengeSkillRequest]
    ] = None


class ChallengeStatusRequest(BaseModel):
    status: ChallengeStatus







class ChallengeResponse(BaseModel):
    id: UUID

    employer_id: UUID

    title: str

    company_name: str

    description: str

    instructions: str

    deliverables: Optional[str]

    challenge_type: ChallengeType

    difficulty: ChallengeDifficulty

    status: ChallengeStatus

    deadline: Optional[date]

    skills: List[
        ChallengeSkillResponse
    ]

    created_at: datetime

    updated_at: datetime


class ChallengeListResponse(BaseModel):
    items: List[
        ChallengeResponse
    ]

    total: int

    limit: int

    offset: int







class ChallengeSubmissionCreateRequest(
    BaseModel
):
    submission_text: Optional[str] = Field(
        default=None,
        max_length=15000,
    )

    repository_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    demo_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )







class ChallengeSubmissionReviewRequest(
    BaseModel
):
    status: ChallengeSubmissionStatus

    score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )

    employer_feedback: Optional[str] = Field(
        default=None,
        max_length=5000,
    )







class StudentChallengeSubmissionResponse(
    BaseModel
):
    id: UUID

    challenge_id: UUID

    challenge_title: str

    company_name: str

    status: ChallengeSubmissionStatus

    submission_text: Optional[str]

    repository_url: Optional[str]

    demo_url: Optional[str]

    score: Optional[int]

    employer_feedback: Optional[str]

    created_at: datetime

    updated_at: datetime


class StudentChallengeSubmissionListResponse(
    BaseModel
):
    items: List[
        StudentChallengeSubmissionResponse
    ]

    total: int

    limit: int

    offset: int







class EmployerChallengeSubmissionResponse(
    BaseModel
):
    id: UUID

    challenge_id: UUID

    student_id: UUID

    student_name: str

    student_email: str

    status: ChallengeSubmissionStatus

    submission_text: Optional[str]

    repository_url: Optional[str]

    demo_url: Optional[str]

    profile_snapshot: Dict[
        str,
        Any,
    ]

    score: Optional[int]

    employer_feedback: Optional[str]

    reviewed_at: Optional[datetime]

    created_at: datetime

    updated_at: datetime


class EmployerChallengeSubmissionListResponse(
    BaseModel
):
    items: List[
        EmployerChallengeSubmissionResponse
    ]

    total: int

    limit: int

    offset: int