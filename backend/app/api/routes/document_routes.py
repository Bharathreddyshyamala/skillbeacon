from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.document import DocumentType
from app.models.user import User, UserRole
from app.repositories.document_repository import (
    count_user_documents,
    get_document_by_id,
    get_user_documents,
    get_user_storage_usage,
)
from app.schemas.document_schema import (
    DocumentDownloadResponse,
    DocumentListResponse,
    DocumentResponse,
    StorageQuotaResponse,
)
from app.services.storage_service import (
    delete_document,
    generate_presigned_download_url,
    replace_employer_logo,
    replace_student_resume,
    upload_document,
)


router = APIRouter(prefix="/documents", tags=["Document & File Storage"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.GENERAL),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """
    Upload a general file or document, store in Cloudflare R2 / S3, and record
    metadata in PostgreSQL.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file",
        )

    doc = upload_document(
        db=db,
        user=current_user,
        file_bytes=file_bytes,
        file_name=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        document_type=document_type,
    )
    return DocumentResponse.model_validate(doc)


@router.post(
    "/upload-resume",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_student_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """
    Upload a Student Resume (PDF/DOCX), store in Cloudflare R2, and update
    student_profile.resume_path to the new active resume while retaining the document in the user's library.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file",
        )

    doc = replace_student_resume(
        db=db,
        user=current_user,
        file_bytes=file_bytes,
        file_name=file.filename or "resume.pdf",
        content_type=file.content_type or "application/pdf",
    )
    return DocumentResponse.model_validate(doc)


@router.post(
    "/upload-logo",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """
    Upload an Employer Company Logo (PNG/JPG/WEBP/SVG), store in Cloudflare R2,
    and update employer_profile.logo_path.
    """
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file",
        )

    doc = replace_employer_logo(
        db=db,
        user=current_user,
        file_bytes=file_bytes,
        file_name=file.filename or "logo.png",
        content_type=file.content_type or "image/png",
    )
    return DocumentResponse.model_validate(doc)


@router.get(
    "/my-documents",
    response_model=DocumentListResponse,
)
def list_my_documents(
    document_type: Optional[DocumentType] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    """
    Paginated on-demand list of active documents for the authenticated user.
    """
    skip = (page - 1) * limit
    items = get_user_documents(
        db=db,
        user_id=current_user.id,
        document_type=document_type,
        skip=skip,
        limit=limit,
    )
    total = count_user_documents(
        db=db,
        user_id=current_user.id,
        document_type=document_type,
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(doc) for doc in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/quota",
    response_model=StorageQuotaResponse,
)
def get_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StorageQuotaResponse:
    """
    Retrieve current storage usage and cumulative quota metrics.
    """
    used_bytes = get_user_storage_usage(db, current_user.id)
    quota_mb = (
        settings.employer_storage_quota_mb
        if current_user.role == UserRole.EMPLOYER
        else settings.user_storage_quota_mb
    )
    used_mb = round(used_bytes / (1024 * 1024), 2)
    percent_used = round((used_bytes / (quota_mb * 1024 * 1024)) * 100, 2)

    return StorageQuotaResponse(
        user_id=current_user.id,
        used_bytes=used_bytes,
        used_mb=used_mb,
        quota_mb=quota_mb,
        percent_used=min(percent_used, 100.0),
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )
    return DocumentResponse.model_validate(doc)


@router.get(
    "/{document_id}/download",
    response_model=DocumentDownloadResponse,
)
def get_download_link(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentDownloadResponse:
    """
    Generate a secure presigned access URL for downloading/viewing a stored document.
    """
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )

    download_url = generate_presigned_download_url(doc.storage_key)
    return DocumentDownloadResponse(
        id=doc.id,
        file_name=doc.file_name,
        download_url=download_url,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a document from Cloudflare R2 storage and remove its record in Postgres.
    """
    delete_document(db=db, user=current_user, document_id=document_id)
