from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.skill import (
    EvidenceType,
    SkillLevel,
    VerificationStatus,
)


class SkillCreateRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
    )
    category: Optional[str] = Field(
        default=None,
        max_length=120,
    )
    description: Optional[str] = None


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserSkillCreateRequest(BaseModel):
    skill_id: UUID
    level: SkillLevel


class UserSkillUpdateRequest(BaseModel):
    level: SkillLevel


class VerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    verifier_id: UUID
    status: VerificationStatus
    comments: Optional[str]
    created_at: datetime
    updated_at: datetime


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_skill_id: UUID
    evidence_type: EvidenceType
    title: str
    description: Optional[str]
    url: Optional[str]
    score: Optional[float]
    status: VerificationStatus
    verifications: List[VerificationResponse] = []
    created_at: datetime
    updated_at: datetime


class EvidenceCreateRequest(BaseModel):
    evidence_type: EvidenceType
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: Optional[str] = None
    url: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )


class VerificationCreateRequest(BaseModel):
    status: VerificationStatus
    comments: Optional[str] = None


class UserSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    skill_id: UUID
    level: SkillLevel
    confidence_score: float
    skill: SkillResponse
    evidence: List[EvidenceResponse] = []
    created_at: datetime
    updated_at: datetime

class EvidenceReviewItem(BaseModel):
    id: UUID
    user_skill_id: UUID

    owner_id: UUID
    owner_email: str

    skill_name: str
    level: SkillLevel

    evidence_type: EvidenceType
    title: str

    description: Optional[str]
    url: Optional[str]

    score: Optional[float]

    status: VerificationStatus

    created_at: datetime