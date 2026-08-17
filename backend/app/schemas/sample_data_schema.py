from datetime import datetime

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from uuid import UUID

from pydantic import BaseModel


class SampleDataValidationError(
    BaseModel
):
    sheet: str
    row: Optional[int] = None
    field: Optional[str] = None
    message: str


class SampleDataPreviewResponse(
    BaseModel
):
    valid: bool
    row_counts: Dict[str, int]
    errors: List[
        SampleDataValidationError
    ]


class SampleDataImportResponse(
    BaseModel
):
    batch_id: UUID
    status: str
    row_counts: Dict[str, int]
    message: str


class SampleDataBatchResponse(
    BaseModel
):
    id: UUID
    source_filename: str
    status: str

    row_counts: Optional[
        Dict[str, Any]
    ] = None

    validation_errors: Optional[
        List[Any]
    ] = None

    storage_cleanup_errors: Optional[
        List[Any]
    ] = None

    created_at: datetime

    completed_at: Optional[
        datetime
    ] = None

    deleted_at: Optional[
        datetime
    ] = None

    class Config:
        from_attributes = True


class SampleDataBatchListResponse(
    BaseModel
):
    items: List[
        SampleDataBatchResponse
    ]


class SampleDataDeleteResponse(
    BaseModel
):
    batch_id: UUID
    status: str
    deleted_records: int
    deleted_objects: int
    storage_errors: List[str]