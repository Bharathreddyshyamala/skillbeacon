from datetime import (
    datetime,
    timezone,
)

from typing import (
    Any,
    Dict,
    List,
)

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy import (
    and_,
    delete,
)

from sqlalchemy.orm import Session

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.sample_data_repository import (
    get_batch,
    get_batch_objects,
    get_batch_records,
)

from app.services.sample_data.constants import (
    DELETE_PRIORITY,
)

from app.services.sample_data.helpers import (
    coerce_value,
    has_column,
    model_for_table,
    optional_model_for_table,
)

from app.services.storage_service import (
    delete_object,
)


def _ensure_admin(
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


def _priority(
    table_name: str,
):

    return DELETE_PRIORITY.get(
        table_name,
        600,
    )


def _delete_record(
    db: Session,
    model,
    pk_values: Dict[
        str,
        Any,
    ],
):

    conditions = []

    for (
        key,
        value,
    ) in pk_values.items():

        if not has_column(
            model,
            key,
        ):
            continue

        typed = coerce_value(
            model,
            key,
            value,
        )

        conditions.append(
            getattr(
                model,
                key,
            )
            ==
            typed
        )

    if not conditions:
        return 0

    result = db.execute(
        delete(
            model
        )
        .where(
            and_(
                *conditions
            )
        )
    )

    return (
        result.rowcount
        or 0
    )


def _sample_user_ids(
    records,
):

    ids = []

    for record in records:

        if (
            record.table_name
            != "users"
        ):
            continue

        value = (
            record.pk_values
            .get(
                "id"
            )
        )

        if value:
            ids.append(value)

    return ids


def _delete_refresh_tokens(
    db: Session,
    user_ids,
):

    model = (
        optional_model_for_table(
            "refresh_tokens"
        )
    )

    if (
        not model
        or not user_ids
        or not has_column(
            model,
            "user_id",
        )
    ):
        return 0

    typed_ids = [
        coerce_value(
            model,
            "user_id",
            value,
        )
        for value
        in user_ids
    ]

    result = db.execute(
        delete(
            model
        )
        .where(
            model.user_id.in_(
                typed_ids
            )
        )
    )

    return (
        result.rowcount
        or 0
    )


def delete_sample_data_batch(
    db: Session,
    current_user: User,
    batch_id,
):

    _ensure_admin(
        current_user
    )

    batch = get_batch(
        db,
        batch_id,
    )

    if not batch:

        raise HTTPException(
            status_code=404,
            detail=(
                "Sample-data batch "
                "not found."
            ),
        )

    if batch.status == "deleted":

        raise HTTPException(
            status_code=409,
            detail=(
                "Sample-data batch "
                "was already deleted."
            ),
        )

    if batch.status not in {
        "completed",
        "deleted_with_storage_errors",
    }:

        raise HTTPException(
            status_code=409,
            detail=(
                "This sample-data batch "
                "cannot currently be deleted."
            ),
        )

    records = get_batch_records(
        db,
        batch_id,
    )

    objects = get_batch_objects(
        db,
        batch_id,
    )

    deleted_records = 0

    database_already_deleted = (
        batch.deleted_at
        is not None
    )

    if not database_already_deleted:

        try:

            user_ids = (
                _sample_user_ids(
                    records
                )
            )

            deleted_records += (
                _delete_refresh_tokens(
                    db,
                    user_ids,
                )
            )

            ordered = sorted(
                records,
                key=lambda record:
                    _priority(
                        record.table_name
                    ),
                reverse=True,
            )

            for record in ordered:

                if (
                    record.table_name
                    .startswith(
                        "sample_data_"
                    )
                ):
                    continue

                model = (
                    model_for_table(
                        record.table_name
                    )
                )

                deleted_records += (
                    _delete_record(
                        db,
                        model,
                        record.pk_values,
                    )
                )

            batch.deleted_at = (
                datetime.now(
                    timezone.utc
                )
            )

            batch.status = (
                "deleted"
            )

            db.commit()

        except Exception as exc:

            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    "Database sample-data "
                    "deletion failed: "
                    f"{exc}"
                ),
            )

    deleted_objects = 0
    storage_errors: List[str] = []

    for obj in objects:

        if obj.deleted_at:
            continue

        try:

            delete_object(
                obj.object_key
            )

            obj.deleted_at = (
                datetime.now(
                    timezone.utc
                )
            )

            deleted_objects += 1

        except Exception as exc:

            storage_errors.append(
                (
                    f"{obj.object_key}: "
                    f"{exc}"
                )
            )

    if storage_errors:

        batch.status = (
            "deleted_with_storage_errors"
        )

        batch.storage_cleanup_errors = (
            storage_errors
        )

    else:

        batch.status = "deleted"

        batch.storage_cleanup_errors = (
            None
        )

    db.commit()

    return {
        "batch_id":
            batch.id,

        "status":
            batch.status,

        "deleted_records":
            deleted_records,

        "deleted_objects":
            deleted_objects,

        "storage_errors":
            storage_errors,
    }