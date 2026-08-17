import uuid

from typing import (
    List,
    Optional,
)

from sqlalchemy import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.models.sample_data import (
    SampleDataBatch,
    SampleDataObject,
    SampleDataRecord,
)


def create_batch(
    db: Session,
    admin_id,
    filename: str,
) -> SampleDataBatch:

    batch = SampleDataBatch(
        uploaded_by_admin_id=admin_id,
        source_filename=filename,
        status="importing",
    )

    db.add(batch)
    db.flush()

    return batch


def get_batch(
    db: Session,
    batch_id,
) -> Optional[SampleDataBatch]:

    return db.get(
        SampleDataBatch,
        batch_id,
    )


def list_batches(
    db: Session,
) -> List[SampleDataBatch]:

    statement = (
        select(
            SampleDataBatch
        )
        .order_by(
            SampleDataBatch
            .created_at
            .desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def track_model_record(
    db: Session,
    batch_id,
    logical_key: str,
    instance,
) -> SampleDataRecord:

    state = inspect(instance)

    pk_values = {}

    for column in (
        state.mapper.primary_key
    ):
        value = getattr(
            instance,
            column.key,
        )

        if isinstance(
            value,
            uuid.UUID,
        ):
            value = str(value)

        pk_values[
            column.key
        ] = value

    record = SampleDataRecord(
        batch_id=batch_id,
        table_name=(
            instance.__tablename__
        ),
        logical_key=logical_key,
        pk_values=pk_values,
    )

    db.add(record)

    return record


def track_storage_object(
    db: Session,
    batch_id,
    bucket_name: str,
    object_key: str,
    content_type: str,
    size_bytes: int,
) -> SampleDataObject:

    obj = SampleDataObject(
        batch_id=batch_id,
        bucket_name=bucket_name,
        object_key=object_key,
        content_type=content_type,
        size_bytes=size_bytes,
    )

    db.add(obj)

    return obj


def get_batch_records(
    db: Session,
    batch_id,
):

    statement = (
        select(
            SampleDataRecord
        )
        .where(
            SampleDataRecord.batch_id
            == batch_id
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def get_batch_objects(
    db: Session,
    batch_id,
):

    statement = (
        select(
            SampleDataObject
        )
        .where(
            SampleDataObject.batch_id
            == batch_id
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )