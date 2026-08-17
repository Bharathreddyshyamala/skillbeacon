import os
import re
import uuid

from datetime import (
    datetime,
    timezone,
)

from uuid import UUID

import boto3

from botocore.config import Config

from botocore.exceptions import (
    ClientError,
)

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.document import (
    Document,
    DocumentType,
)

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.document_repository import (
    create_document,
    delete_document_record,
    get_active_logos_for_user,
    get_document_by_id,
    get_user_storage_usage,
)


DOCUMENT_CONSTRAINTS = {
    DocumentType.RESUME: {
        "extensions": {
            ".pdf",
            ".docx",
            ".doc",
        },
        "mime_types": {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "application/octet-stream",
        },
        "max_size_bytes":
            5 * 1024 * 1024,
    },

    DocumentType.EMPLOYER_LOGO: {
        "extensions": {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".svg",
        },
        "mime_types": {
            "image/png",
            "image/jpeg",
            "image/webp",
            "image/svg+xml",
        },
        "max_size_bytes":
            2 * 1024 * 1024,
    },

    DocumentType.SKILL_EVIDENCE: {
        "extensions": {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        },
        "mime_types": {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/webp",
        },
        "max_size_bytes":
            10 * 1024 * 1024,
    },

    DocumentType.CHALLENGE_SUBMISSION: {
        "extensions": {
            ".pdf",
            ".zip",
            ".png",
            ".jpg",
            ".jpeg",
        },
        "mime_types": {
            "application/pdf",
            "application/zip",
            "application/x-zip-compressed",
            "image/png",
            "image/jpeg",
        },
        "max_size_bytes":
            25 * 1024 * 1024,
    },

    DocumentType.GENERAL: {
        "extensions": {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".docx",
        },
        "mime_types": {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
        "max_size_bytes":
            10 * 1024 * 1024,
    },
}


def _get_s3_client():

    return boto3.client(
        "s3",
        endpoint_url=(
            settings.r2_endpoint_url
        ),
        aws_access_key_id=(
            settings.r2_access_key_id
        ),
        aws_secret_access_key=(
            settings.r2_secret_access_key
        ),
        region_name="auto",
        config=Config(
            signature_version="s3v4"
        ),
    )


def upload_bytes(
    object_key: str,
    data: bytes,
    content_type: str = (
        "application/octet-stream"
    ),
) -> None:

    if not object_key:
        raise ValueError(
            "R2 object key is required."
        )

    if data is None:
        raise ValueError(
            (
                "File data cannot "
                "be None."
            )
        )

    s3 = _get_s3_client()

    try:

        s3.put_object(
            Bucket=(
                settings.r2_bucket_name
            ),
            Key=object_key,
            Body=data,
            ContentType=(
                content_type
                or
                "application/octet-stream"
            ),
        )

    except ClientError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Failed to upload object "
                "to Cloudflare R2."
            ),
        ) from exc


def delete_object(
    object_key: str,
) -> None:

    if not object_key:
        raise ValueError(
            "R2 object key is required."
        )

    s3 = _get_s3_client()

    try:

        s3.delete_object(
            Bucket=(
                settings.r2_bucket_name
            ),
            Key=object_key,
        )

    except ClientError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Failed to delete object "
                "from Cloudflare R2."
            ),
        ) from exc


def sanitize_filename(
    filename: str,
) -> str:

    clean = os.path.basename(
        filename
    )

    clean = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        clean,
    )

    return clean[:100]


def validate_file_upload(
    filename: str,
    content_type: str,
    file_size: int,
    document_type: DocumentType,
) -> None:

    constraints = (
        DOCUMENT_CONSTRAINTS.get(
            document_type,
            DOCUMENT_CONSTRAINTS[
                DocumentType.GENERAL
            ],
        )
    )

    _, extension = os.path.splitext(
        filename.lower()
    )

    if (
        extension
        not in constraints[
            "extensions"
        ]
    ):

        allowed = ", ".join(
            sorted(
                constraints[
                    "extensions"
                ]
            )
        )

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                f"Invalid file extension "
                f"'{extension}' for "
                f"{document_type.value}. "
                f"Allowed extensions: "
                f"{allowed}"
            ),
        )

    if (
        content_type
        and content_type
        not in constraints[
            "mime_types"
        ]
    ):

        allowed_mimes = ", ".join(
            sorted(
                constraints[
                    "mime_types"
                ]
            )
        )

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                f"Unsupported content type "
                f"'{content_type}' for "
                f"{document_type.value}. "
                f"Allowed types: "
                f"{allowed_mimes}"
            ),
        )

    if (
        file_size
        >
        constraints[
            "max_size_bytes"
        ]
    ):

        max_mb = (
            constraints[
                "max_size_bytes"
            ]
            /
            (1024 * 1024)
        )

        raise HTTPException(
            status_code=(
                status
                .HTTP_413_REQUEST_ENTITY_TOO_LARGE
            ),
            detail=(
                "File exceeds maximum "
                f"allowed size of "
                f"{max_mb:.1f} MB for "
                f"{document_type.value}."
            ),
        )


def check_user_quota(
    db: Session,
    user: User,
    new_file_size: int,
) -> None:

    current_usage = (
        get_user_storage_usage(
            db,
            user.id,
        )
    )

    if (
        user.role
        == UserRole.EMPLOYER
    ):

        max_quota_mb = (
            settings
            .employer_storage_quota_mb
        )

    else:

        max_quota_mb = (
            settings
            .user_storage_quota_mb
        )

    max_quota_bytes = (
        max_quota_mb
        * 1024
        * 1024
    )

    if (
        current_usage
        + new_file_size
        >
        max_quota_bytes
    ):

        raise HTTPException(
            status_code=(
                status
                .HTTP_413_REQUEST_ENTITY_TOO_LARGE
            ),
            detail=(
                "Storage quota exceeded "
                f"({max_quota_mb} MB limit). "
                f"Current usage: "
                f"{current_usage / (1024 * 1024):.2f} MB. "
                "Please delete older "
                "documents to upload "
                "new ones."
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

    file_size = len(
        file_bytes
    )

    validate_file_upload(
        filename=file_name,
        content_type=content_type,
        file_size=file_size,
        document_type=document_type,
    )

    check_user_quota(
        db=db,
        user=user,
        new_file_size=file_size,
    )

    safe_name = sanitize_filename(
        file_name
    )

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    unique_id = (
        uuid.uuid4()
        .hex[:8]
    )

    storage_key = (
        f"{document_type.value}s/"
        f"{user.id}/"
        f"{timestamp}_"
        f"{unique_id}_"
        f"{safe_name}"
    )

    upload_bytes(
        object_key=storage_key,
        data=file_bytes,
        content_type=(
            content_type
            or
            "application/octet-stream"
        ),
    )

    base_url = (
        settings
        .r2_public_base_url
        .rstrip("/")
    )

    file_url = (
        f"{base_url}/"
        f"{storage_key}"
    )

    document = create_document(
        db=db,
        user_id=user.id,
        document_type=document_type,
        storage_key=storage_key,
        file_name=file_name,
        file_url=file_url,
        mime_type=(
            content_type
            or
            "application/octet-stream"
        ),
        size_bytes=file_size,
    )

    return document


def generate_presigned_download_url(
    storage_key: str,
    expires_in: int = 3600,
) -> str:

    if not storage_key:

        raise ValueError(
            (
                "Storage key "
                "is required."
            )
        )

    s3 = _get_s3_client()

    try:

        url = (
            s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket":
                        settings
                        .r2_bucket_name,

                    "Key":
                        storage_key,
                },
                ExpiresIn=(
                    expires_in
                ),
            )
        )

        return url

    except ClientError as exc:

        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Could not generate "
                "access URL."
            ),
        ) from exc


def delete_document(
    db: Session,
    user: User,
    document_id: UUID,
) -> None:

    document = (
        get_document_by_id(
            db,
            document_id,
        )
    )

    if not document:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Document not found"
            ),
        )

    if (
        document.user_id
        != user.id
        and
        user.role
        != UserRole.ADMIN
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "You do not have "
                "permission to delete "
                "this document"
            ),
        )

    try:

        delete_object(
            document.storage_key
        )

    except HTTPException:

        pass

    delete_document_record(
        db,
        document,
    )


def replace_student_resume(
    db: Session,
    user: User,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
) -> Document:

    new_document = (
        upload_document(
            db=db,
            user=user,
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type,
            document_type=(
                DocumentType.RESUME
            ),
        )
    )

    if user.student_profile:

        user.student_profile.resume_path = (
            new_document.file_url
        )

        db.commit()

        db.refresh(
            user.student_profile
        )

    return new_document


def replace_employer_logo(
    db: Session,
    user: User,
    file_bytes: bytes,
    file_name: str,
    content_type: str,
) -> Document:

    old_logos = (
        get_active_logos_for_user(
            db,
            user.id,
        )
    )

    for old_document in old_logos:

        try:

            delete_object(
                old_document.storage_key
            )

        except HTTPException:

            pass

        delete_document_record(
            db,
            old_document,
        )

    new_document = (
        upload_document(
            db=db,
            user=user,
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type,
            document_type=(
                DocumentType
                .EMPLOYER_LOGO
            ),
        )
    )

    if user.employer_profile:

        user.employer_profile.logo_path = (
            new_document.file_url
        )

        db.commit()

        db.refresh(
            user.employer_profile
        )

    return new_document