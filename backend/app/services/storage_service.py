import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, Set, Tuple
from uuid import UUID

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentType
from app.models.user import User, UserRole
from app.repositories.document_repository import (
    create_document,
    delete_document_record,
    get_active_logos_for_user,
    get_active_resumes_for_user,
    get_document_by_id,
    get_user_storage_usage,
)


# ==============================================================================
# Allowed MIME types and size limits per DocumentType
# ==============================================================================

DOCUMENT_CONSTRAINTS = {
    DocumentType.RESUME: {
        "extensions": {".pdf", ".docx", ".doc"},
        "mime_types": {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "application/octet-stream",
        },
        "max_size_bytes": 5 * 1024 * 1024,  # 5 MB
    },
    DocumentType.EMPLOYER_LOGO: {
        "extensions": {".png", ".jpg", ".jpeg", ".webp", ".svg"},
        "mime_types": {
            "image/png",
            "image/jpeg",
            "image/webp",
            "image/svg+xml",
        },
        "max_size_bytes": 2 * 1024 * 1024,  # 2 MB
    },
    DocumentType.SKILL_EVIDENCE: {
        "extensions": {".pdf", ".png", ".jpg", ".jpeg", ".webp"},
        "mime_types": {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/webp",
        },
        "max_size_bytes": 10 * 1024 * 1024,  # 10 MB
    },
    DocumentType.CHALLENGE_SUBMISSION: {
        "extensions": {".pdf", ".zip", ".png", ".jpg", ".jpeg"},
        "mime_types": {
            "application/pdf",
            "application/zip",
            "application/x-zip-compressed",
            "image/png",
            "image/jpeg",
        },
        "max_size_bytes": 25 * 1024 * 1024,  # 25 MB
    },
    DocumentType.GENERAL: {
        "extensions": {".pdf", ".png", ".jpg", ".jpeg", ".docx"},
        "mime_types": {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
        "max_size_bytes": 10 * 1024 * 1024,  # 10 MB
    },
}


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename removing path traversal and unsafe characters.
    """
    clean = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9._-]", "_", clean)
    return clean[:100]


def validate_file_upload(
    filename: str,
    content_type: str,
    file_size: int,
    document_type: DocumentType,
) -> None:
    constraints = DOCUMENT_CONSTRAINTS.get(
        document_type,
        DOCUMENT_CONSTRAINTS[DocumentType.GENERAL],
    )
    _, ext = os.path.splitext(filename.lower())

    if ext not in constraints["extensions"]:
        allowed = ", ".join(sorted(constraints["extensions"]))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid file extension '{ext}' for {document_type.value}. "
                f"Allowed extensions: {allowed}"
            ),
        )

    if content_type and content_type not in constraints["mime_types"]:
        allowed_mimes = ", ".join(sorted(constraints["mime_types"]))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported content type '{content_type}' for {document_type.value}. "
                f"Allowed types: {allowed_mimes}"
            ),
        )

    if file_size > constraints["max_size_bytes"]:
        max_mb = constraints["max_size_bytes"] / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {max_mb:.1f} MB for {document_type.value}.",
        )


def check_user_quota(
    db: Session,
    user: User,
    new_file_size: int,
) -> None:
    current_usage = get_user_storage_usage(db, user.id)
    max_quota_mb = (
        settings.employer_storage_quota_mb
        if user.role == UserRole.EMPLOYER
        else settings.user_storage_quota_mb
    )
    max_quota_bytes = max_quota_mb * 1024 * 1024

    if current_usage + new_file_size > max_quota_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Storage quota exceeded ({max_quota_mb} MB limit). "
                f"Current usage: {current_usage / (1024 * 1024):.2f} MB. "
                "Please delete older documents to upload new ones."
            ),
        )


def upload_document(
    db: Session,
    user: User,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
    document_type: DocumentType,
) -> Document:
    file_size = len(file_bytes)
    validate_file_upload(file_name, content_type, file_size, document_type)
    check_user_quota(db, user, file_size)

    safe_name = sanitize_filename(file_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    storage_key = f"{document_type.value}s/{user.id}/{timestamp}_{unique_id}_{safe_name}"

    s3 = _get_s3_client()
    try:
        s3.put_object(
            Bucket=settings.r2_bucket_name,
            Key=storage_key,
            Body=file_bytes,
            ContentType=content_type or "application/octet-stream",
        )
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload document to cloud storage: {exc}",
        ) from exc

    # Generate access URL
    base_url = settings.r2_public_base_url.rstrip("/")
    file_url = f"{base_url}/{storage_key}"

    document = create_document(
        db=db,
        user_id=user.id,
        document_type=document_type,
        storage_key=storage_key,
        file_name=file_name,
        file_url=file_url,
        mime_type=content_type or "application/octet-stream",
        size_bytes=file_size,
    )

    return document


def generate_presigned_download_url(
    storage_key: str,
    expires_in: int = 3600,
) -> str:
    s3 = _get_s3_client()
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.r2_bucket_name,
                "Key": storage_key,
            },
            ExpiresIn=expires_in,
        )
        return url
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not generate access URL: {exc}",
        ) from exc


def delete_document(
    db: Session,
    user: User,
    document_id: UUID,
) -> None:
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Only document owner or Admin can delete
    if document.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this document",
        )

    # Delete from R2
    s3 = _get_s3_client()
    try:
        s3.delete_object(
            Bucket=settings.r2_bucket_name,
            Key=document.storage_key,
        )
    except ClientError:
        pass  # Continue to delete DB record even if cloud object was already gone

    delete_document_record(db, document)


def replace_student_resume(
    db: Session,
    user: User,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
) -> Document:
    """
    Upload a new resume to the student's multi-resume document library in Cloudflare R2,
    and update student_profile.resume_path to this new primary resume.
    """
    # 1. Upload new resume to R2 and Postgres library (without deleting previous resumes)
    new_doc = upload_document(
        db=db,
        user=user,
        file_bytes=file_bytes,
        file_name=file_name,
        content_type=content_type,
        document_type=DocumentType.RESUME,
    )

    # 2. Update student profile resume_path to point to the newest primary resume
    if user.student_profile:
        user.student_profile.resume_path = new_doc.file_url
        db.commit()
        db.refresh(user.student_profile)

    return new_doc


def replace_employer_logo(
    db: Session,
    user: User,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
) -> Document:
    """
    Upload a new employer logo and purge old logo from R2 & DB.
    """
    old_logos = get_active_logos_for_user(db, user.id)
    s3 = _get_s3_client()
    for old_doc in old_logos:
        try:
            s3.delete_object(Bucket=settings.r2_bucket_name, Key=old_doc.storage_key)
        except Exception:
            pass
        delete_document_record(db, old_doc)

    new_doc = upload_document(
        db=db,
        user=user,
        file_bytes=file_bytes,
        file_name=file_name,
        content_type=content_type,
        document_type=DocumentType.EMPLOYER_LOGO,
    )

    if user.employer_profile:
        user.employer_profile.logo_path = new_doc.file_url
        db.commit()
        db.refresh(user.employer_profile)

    return new_doc
