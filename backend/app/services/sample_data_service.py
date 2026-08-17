from datetime import (
    datetime,
    timezone,
)

from typing import List

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy import (
    select,
)

from sqlalchemy.orm import Session

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.sample_data_repository import (
    create_batch,
    get_batch,
    list_batches,
)

from app.services.sample_data.constants import (
    MAX_SAMPLE_WORKBOOK_BYTES,
)

from app.services.sample_data.context import (
    SampleDataContext,
)

from app.services.sample_data.delete_service import (
    delete_sample_data_batch,
)

from app.services.sample_data_excel_service import (
    read_sample_workbook,
    validate_sample_workbook,
)

from app.services.sample_data_importers import (
    import_applications,
    import_challenges,
    import_challenge_skills,
    import_challenge_submissions,
    import_mentorships,
    import_mentorship_sessions,
    import_notifications,
    import_opportunities,
    import_opportunity_skills,
    import_profiles,
    import_resumes,
    import_skills,
    import_skill_evidence,
    import_skill_verifications,
    import_users,
    import_user_skills,
)

from app.services.storage_service import (
    delete_object,
)


def ensure_admin(
    current_user: User,
):

    if (
        current_user.role
        != UserRole.ADMIN
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Administrator access "
                "is required."
            ),
        )


async def _read_workbook(
    upload: UploadFile,
):

    if not upload.filename:

        raise HTTPException(
            status_code=400,
            detail=(
                "Filename is required."
            ),
        )

    if not (
        upload.filename
        .lower()
        .endswith(
            ".xlsx"
        )
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only .xlsx files "
                "are supported."
            ),
        )

    content = await upload.read()

    await upload.close()

    if not content:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded workbook "
                "is empty."
            ),
        )

    if (
        len(content)
        >
        MAX_SAMPLE_WORKBOOK_BYTES
    ):

        raise HTTPException(
            status_code=413,
            detail=(
                "Workbook must be "
                "10 MB or smaller."
            ),
        )

    try:

        return (
            read_sample_workbook(
                content
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to read workbook: "
                f"{exc}"
            ),
        )


def _row_counts(
    data,
):

    return {
        sheet:
            len(rows)

        for (
            sheet,
            rows,
        ) in data.items()
    }


def _existing_emails(
    db: Session,
    data,
):

    emails = [
        str(
            row[
                "email"
            ]
        )
        .strip()
        .lower()

        for row
        in data.get(
            "users",
            [],
        )

        if row.get(
            "email"
        )
    ]

    if not emails:
        return []

    statement = (
        select(
            User.email
        )
        .where(
            User.email.in_(
                emails
            )
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def _add_database_errors(
    db,
    data,
    errors,
):

    for email in (
        _existing_emails(
            db,
            data,
        )
    ):

        errors.append(
            {
                "sheet":
                    "users",

                "row":
                    None,

                "field":
                    "email",

                "message":
                    (
                        "User already exists: "
                        f"{email}"
                    ),
            }
        )


async def preview_sample_data(
    db: Session,
    current_user: User,
    upload: UploadFile,
):

    ensure_admin(
        current_user
    )

    data = await (
        _read_workbook(
            upload
        )
    )

    errors = (
        validate_sample_workbook(
            data
        )
    )

    _add_database_errors(
        db,
        data,
        errors,
    )

    return {
        "valid":
            len(errors) == 0,

        "row_counts":
            _row_counts(
                data
            ),

        "errors":
            errors,
    }


def _cleanup_r2(
    object_keys: List[str],
):

    errors = []

    for object_key in reversed(
        object_keys
    ):

        try:

            delete_object(
                object_key
            )

        except Exception as exc:

            errors.append(
                (
                    f"{object_key}: "
                    f"{exc}"
                )
            )

    return errors


async def import_sample_data(
    db: Session,
    current_user: User,
    upload: UploadFile,
):

    ensure_admin(
        current_user
    )

    filename = (
        upload.filename
        or
        "sample-data.xlsx"
    )

    data = await (
        _read_workbook(
            upload
        )
    )

    errors = (
        validate_sample_workbook(
            data
        )
    )

    _add_database_errors(
        db,
        data,
        errors,
    )

    if errors:

        raise HTTPException(
            status_code=422,
            detail={
                "message":
                    (
                        "Workbook validation "
                        "failed."
                    ),

                "errors":
                    errors,
            },
        )

    counts = _row_counts(
        data
    )

    batch = create_batch(
        db=db,
        admin_id=current_user.id,
        filename=filename,
    )

    db.commit()
    db.refresh(batch)

    context = (
        SampleDataContext()
    )

    try:

        import_users(
            db,
            batch,
            data["users"],
            context,
        )

        import_profiles(
            db,
            batch,
            data["profiles"],
            context,
        )

        import_skills(
            db,
            batch,
            data["skills"],
            context,
        )

        import_user_skills(
            db,
            batch,
            data["user_skills"],
            context,
        )

        import_skill_evidence(
            db,
            batch,
            data[
                "skill_evidence"
            ],
            context,
        )

        import_skill_verifications(
            db,
            batch,
            data[
                "skill_verifications"
            ],
            context,
        )

        import_resumes(
            db,
            batch,
            data[
                "resume_files"
            ],
            context,
        )

        import_opportunities(
            db,
            batch,
            data[
                "opportunities"
            ],
            context,
        )

        import_opportunity_skills(
            db,
            batch,
            data[
                "opportunity_skills"
            ],
            context,
        )

        import_applications(
            db,
            batch,
            data[
                "applications"
            ],
            context,
        )

        import_mentorships(
            db,
            batch,
            data[
                "mentorships"
            ],
            context,
        )

        import_mentorship_sessions(
            db,
            batch,
            data[
                "mentorship_sessions"
            ],
            context,
        )

        import_challenges(
            db,
            batch,
            data[
                "challenges"
            ],
            context,
        )

        import_challenge_skills(
            db,
            batch,
            data[
                "challenge_skills"
            ],
            context,
        )

        import_challenge_submissions(
            db,
            batch,
            data[
                "challenge_submissions"
            ],
            context,
        )

        import_notifications(
            db,
            batch,
            data[
                "notifications"
            ],
            context,
        )

        batch.status = (
            "completed"
        )

        batch.row_counts = counts

        batch.completed_at = (
            datetime.now(
                timezone.utc
            )
        )

        db.commit()
        db.refresh(batch)

        return {
            "batch_id":
                batch.id,

            "status":
                batch.status,

            "row_counts":
                counts,

            "message":
                (
                    "Sample data imported "
                    "successfully."
                ),
        }

    except Exception as exc:

        db.rollback()

        cleanup_errors = (
            _cleanup_r2(
                context
                .uploaded_r2_keys
            )
        )

        try:

            failed_batch = (
                get_batch(
                    db,
                    batch.id,
                )
            )

            if failed_batch:

                failed_batch.status = (
                    "failed"
                )

                failed_batch.row_counts = (
                    counts
                )

                failed_batch.validation_errors = [
                    {
                        "message":
                            str(exc)
                    }
                ]

                failed_batch.storage_cleanup_errors = (
                    cleanup_errors
                    or None
                )

                failed_batch.completed_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                db.commit()

        except Exception:

            db.rollback()

        if isinstance(
            exc,
            HTTPException,
        ):
            raise

        raise HTTPException(
            status_code=500,
            detail=(
                "Sample-data import "
                f"failed: {exc}"
            ),
        )


def get_sample_data_batches(
    db: Session,
    current_user: User,
):

    ensure_admin(
        current_user
    )

    return {
        "items":
            list_batches(
                db
            )
    }


def remove_sample_data_batch(
    db: Session,
    current_user: User,
    batch_id,
):

    return (
        delete_sample_data_batch(
            db=db,
            current_user=(
                current_user
            ),
            batch_id=batch_id,
        )
    )