from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentType


class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    document_type: DocumentType
    storage_key: str = Field(exclude=True)
    file_name: str
    file_url: str
    mime_type: str
    size_bytes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentDownloadResponse(BaseModel):
    id: UUID
    file_name: str
    download_url: str
    mime_type: str
    size_bytes: int


class StorageQuotaResponse(BaseModel):
    user_id: UUID
    used_bytes: int
    used_mb: float
    quota_mb: int
    percent_used: float


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    limit: int
