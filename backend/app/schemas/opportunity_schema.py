from datetime import date, datetime

from typing import (
    List,
    Optional,
)

from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.opportunity import (
    EmploymentType,
    OpportunityStatus,
    OpportunityType,
    WorkMode,
)

from app.models.skill import (
    SkillLevel,
)

from app.schemas.skill_schema import (
    SkillResponse,
)




class OpportunitySkillRequest(BaseModel):

    skill_id: UUID

    minimum_level: SkillLevel = (
        SkillLevel.BEGINNER
    )

    required: bool = True




class OpportunitySkillResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    skill_id: UUID

    minimum_level: SkillLevel

    required: bool

    skill: SkillResponse




class OpportunityCreateRequest(BaseModel):

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    company_name: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str = Field(
        min_length=20,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    work_mode: WorkMode

    opportunity_type: OpportunityType

    employment_type: Optional[
        EmploymentType
    ] = None

    salary_min: Optional[float] = Field(
        default=None,
        ge=0,
    )

    salary_max: Optional[float] = Field(
        default=None,
        ge=0,
    )

    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
    )

    application_url: Optional[str] = None

    deadline: Optional[date] = None

    status: OpportunityStatus = (
        OpportunityStatus.DRAFT
    )

    skills: List[
        OpportunitySkillRequest
    ] = Field(
        default_factory=list
    )




class OpportunityUpdateRequest(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    company_name: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    description: Optional[str] = None

    location: Optional[str] = None

    work_mode: Optional[
        WorkMode
    ] = None

    opportunity_type: Optional[
        OpportunityType
    ] = None

    employment_type: Optional[
        EmploymentType
    ] = None

    salary_min: Optional[float] = Field(
        default=None,
        ge=0,
    )

    salary_max: Optional[float] = Field(
        default=None,
        ge=0,
    )

    currency: Optional[str] = None

    application_url: Optional[str] = None

    deadline: Optional[date] = None

    skills: Optional[
        List[
            OpportunitySkillRequest
        ]
    ] = None




class OpportunityStatusRequest(BaseModel):

    status: OpportunityStatus




class OpportunityResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    employer_id: UUID

    company_name: str

    title: str

    description: str

    location: Optional[str]

    work_mode: WorkMode

    opportunity_type: OpportunityType

    employment_type: Optional[
        EmploymentType
    ]

    salary_min: Optional[float]

    salary_max: Optional[float]

    currency: str

    application_url: Optional[str]

    deadline: Optional[date]

    status: OpportunityStatus

    created_at: datetime

    updated_at: datetime

    skills: List[
        OpportunitySkillResponse
    ]