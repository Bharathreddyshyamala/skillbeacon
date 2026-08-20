import uuid

from datetime import (
    date,
    datetime,
    time,
    timezone,
)

from typing import (
    Any,
    Dict,
    Optional,
)

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
)

from sqlalchemy.orm import Session

import app.models

from app.models.base import Base

from app.repositories.sample_data_repository import (
    track_model_record,
)


def enum_text(
    value,
) -> Optional[str]:

    if value is None:
        return None

    if hasattr(
        value,
        "value",
    ):
        return str(
            value.value
        )

    return str(value)


def as_bool(
    value,
    default: bool = False,
) -> bool:

    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        (int, float),
    ):
        return bool(value)

    text = str(
        value
    ).strip().lower()

    if text in {
        "true",
        "1",
        "yes",
        "y",
    }:
        return True

    if text in {
        "false",
        "0",
        "no",
        "n",
        "",
    }:
        return False

    return default


def model_for_table(
    table_name: str,
):

    for mapper in (
        Base.registry.mappers
    ):

        model = mapper.class_

        if (
            getattr(
                model,
                "__tablename__",
                None,
            )
            == table_name
        ):
            return model

    raise RuntimeError(
        (
            "No SQLAlchemy model "
            "registered for table: "
            f"{table_name}"
        )
    )


def optional_model_for_table(
    table_name: str,
):

    try:
        return model_for_table(
            table_name
        )

    except RuntimeError:
        return None


def has_column(
    model,
    column_name: str,
) -> bool:

    return (
        column_name
        in model.__table__.columns
    )


def ensure_datetime(
    value,
) -> Optional[datetime]:

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        result = value

    elif isinstance(
        value,
        date,
    ):
        result = datetime.combine(
            value,
            time.min,
        )

    else:
        result = (
            datetime.fromisoformat(
                str(value).strip()
            )
        )

    if (
        result.tzinfo
        is None
    ):
        result = result.replace(
            tzinfo=timezone.utc
        )

    return result


def coerce_value(
    model,
    column_name: str,
    value,
):

    if value in (
        None,
        "",
    ):
        return None

    column = (
        model.__table__
        .columns[
            column_name
        ]
    )

    enum_class = getattr(
        column.type,
        "enum_class",
        None,
    )

    if enum_class:

        if isinstance(
            value,
            enum_class,
        ):
            return value

        try:
            return enum_class(
                value
            )

        except (
            ValueError,
            TypeError,
        ):
            pass

        try:
            return enum_class[
                str(value).upper()
            ]

        except (
            KeyError,
            TypeError,
        ):
            raise ValueError(
                (
                    f"Invalid value "
                    f"'{value}' for "
                    f"{model.__name__}."
                    f"{column_name}"
                )
            )

    if isinstance(
        column.type,
        Boolean,
    ):
        return as_bool(value)

    if isinstance(
        column.type,
        DateTime,
    ):
        return ensure_datetime(
            value
        )

    if isinstance(
        column.type,
        Date,
    ):

        if isinstance(
            value,
            datetime,
        ):
            return value.date()

        if isinstance(
            value,
            date,
        ):
            return value

        return date.fromisoformat(
            str(value)
        )

    try:
        python_type = (
            column.type.python_type
        )

    except Exception:
        python_type = None

    if (
        python_type is uuid.UUID
        and isinstance(
            value,
            str,
        )
    ):
        return uuid.UUID(
            value
        )

    return value


def build_instance(
    model,
    values: Dict[str, Any],
):

    kwargs = {}

    for (
        key,
        value,
    ) in values.items():

        if key == "_row_number":
            continue

        if not has_column(
            model,
            key,
        ):
            continue

        if value in (
            None,
            "",
        ):
            continue

        kwargs[key] = (
            coerce_value(
                model,
                key,
                value,
            )
        )

    return model(
        **kwargs
    )


def set_first_existing(
    model,
    values,
    names,
    value,
    required=True,
):

    for name in names:

        if has_column(
            model,
            name,
        ):
            values[
                name
            ] = value

            return name

    if required:
        raise RuntimeError(
            (
                "Expected one of "
                f"{names} on "
                f"{model.__name__}"
            )
        )

    return None


def add_and_track(
    db: Session,
    batch_id,
    logical_key,
    instance,
):

    db.add(instance)
    db.flush()

    track_model_record(
        db=db,
        batch_id=batch_id,
        logical_key=str(
            logical_key
        ),
        instance=instance,
    )

    return instance