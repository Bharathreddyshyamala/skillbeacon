from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole
from app.schemas.auth_schema import UserResponse


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    headline: Optional[str] = Field(default=None, max_length=200)
    summary: Optional[str] = None
    education: Optional[str] = None
    work_experience: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    work_authorization: Optional[str] = Field(default=None, max_length=100)
    availability: Optional[str] = Field(default=None, max_length=100)
    career_goals: Optional[str] = None
    github_url: Optional[str] = Field(default=None, max_length=500)
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    portfolio_url: Optional[str] = Field(default=None, max_length=500)

    company_name: Optional[str] = Field(default=None, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=150)
    company_size: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=250)

    display_name: Optional[str] = Field(default=None, max_length=200)
    bio: Optional[str] = None
    years_of_experience: Optional[int] = Field(default=None, ge=0, le=80)
    languages: Optional[List[str]] = None
    mentorship_formats: Optional[List[str]] = None
    is_accepting_requests: Optional[bool] = None

    is_public: Optional[bool] = None

    @field_validator(
        "preferred_roles",
        "preferred_locations",
        "languages",
        "mentorship_formats",
    )
    @classmethod
    def clean_list_values(
        cls,
        values: Optional[List[str]],
    ) -> Optional[List[str]]:
        if values is None:
            return None

        return [
            value.strip()
            for value in values
            if value and value.strip()
        ]


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    education: Optional[str]
    work_experience: Optional[str]
    preferred_roles: List[str]
    preferred_locations: List[str]
    work_authorization: Optional[str]
    availability: Optional[str]
    career_goals: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    resume_path: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime


class EmployerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    company_name: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    website: Optional[str]
    description: Optional[str]
    location: Optional[str]
    logo_path: Optional[str]
    verification_status: str
    is_public: bool
    created_at: datetime
    updated_at: datetime


class MentorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    display_name: Optional[str]
    headline: Optional[str]
    bio: Optional[str]
    industry: Optional[str]
    years_of_experience: Optional[int]
    languages: List[str]
    mentorship_formats: List[str]
    availability: Optional[str]
    is_accepting_requests: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime


ProfileData = Union[
    StudentProfileResponse,
    EmployerProfileResponse,
    MentorProfileResponse,
]


class ProfileEnvelope(BaseModel):
    user: UserResponse
    profile_type: UserRole
    profile: ProfileData
