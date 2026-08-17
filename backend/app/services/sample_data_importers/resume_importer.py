from sqlalchemy.orm import Session

from app.core.config import settings

from app.repositories.sample_data_repository import (
    track_storage_object,
)

from app.services.sample_data.helpers import (
    as_bool,
    has_column,
)

from app.services.sample_resume_service import (
    generate_sample_resume_pdf,
)

from app.services.storage_service import (
    upload_bytes,
)


def _bucket_name():

    candidates = [
        "r2_bucket_name",
        "r2_bucket",
        "cloudflare_r2_bucket_name",
        "cloudflare_r2_bucket",
    ]

    for name in candidates:

        value = getattr(
            settings,
            name,
            None,
        )

        if value:
            return str(value)

    raise RuntimeError(
        (
            "R2 bucket configuration "
            "was not found."
        )
    )


def _set_resume_reference(
    profile,
    object_key,
    original_filename,
):

    for field in [
        "resume_object_key",
        "resume_key",
        "resume_path",
    ]:

        if hasattr(
            profile,
            field,
        ):

            setattr(
                profile,
                field,
                object_key,
            )

            break

    for field in [
        "resume_filename",
        "resume_original_filename",
    ]:

        if hasattr(
            profile,
            field,
        ):

            setattr(
                profile,
                field,
                original_filename,
            )

            break


def import_resumes(
    db: Session,
    batch,
    rows,
    context,
):

    bucket = _bucket_name()

    for row in rows:

        if not as_bool(
            row.get(
                "generate_placeholder"
            ),
            True,
        ):

            raise ValueError(
                (
                    "Sample resume rows "
                    "must use "
                    "generate_placeholder=true."
                )
            )

        user = context.get(
            "users",
            row[
                "user_key"
            ],
        )

        profile = (
            context.get_optional(
                "profiles",
                row[
                    "user_key"
                ],
            )
        )

        resume_key = str(
            row[
                "resume_key"
            ]
        )

        original_filename = str(
            row.get(
                "original_filename"
            )
            or
            f"{resume_key}.pdf"
        )

        object_key = (
            f"sample-data/"
            f"{batch.id}/"
            f"resumes/"
            f"{resume_key}.pdf"
        )

        first_name = (
            getattr(
                profile,
                "first_name",
                "",
            )
            if profile
            else ""
        )

        last_name = (
            getattr(
                profile,
                "last_name",
                "",
            )
            if profile
            else ""
        )

        name = (
            f"{first_name} "
            f"{last_name}"
        ).strip()

        if not name:
            name = user.email

        headline = (
            getattr(
                profile,
                "headline",
                "",
            )
            if profile
            else ""
        )

        summary = (
            getattr(
                profile,
                "summary",
                "",
            )
            if profile
            else ""
        )

        pdf = (
            generate_sample_resume_pdf(
                name=name,
                email=user.email,
                headline=headline,
                summary=summary,
            )
        )

        upload_bytes(
            object_key=object_key,
            data=pdf,
            content_type=(
                "application/pdf"
            ),
        )

        context.uploaded_r2_keys.append(
            object_key
        )

        track_storage_object(
            db=db,
            batch_id=batch.id,
            bucket_name=bucket,
            object_key=object_key,
            content_type=(
                "application/pdf"
            ),
            size_bytes=len(pdf),
        )

        if profile:

            _set_resume_reference(
                profile,
                object_key,
                original_filename,
            )

        context.store(
            "resume_files",
            resume_key,
            {
                "object_key":
                    object_key,

                "original_filename":
                    original_filename,

                "content_type":
                    "application/pdf",
            },
        )