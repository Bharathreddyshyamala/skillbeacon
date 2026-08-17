from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
)

from app.models.user import User

from app.services.sample_data.helpers import (
    add_and_track,
    as_bool,
    build_instance,
)


def import_users(
    db: Session,
    batch,
    rows,
    context,
):

    for row in rows:

        role = str(
            row[
                "role"
            ]
        ).strip().lower()

        if role == "admin":
            raise ValueError(
                (
                    "Admin users cannot "
                    "be imported from Excel."
                )
            )

        values = {
            "email":
                str(
                    row[
                        "email"
                    ]
                )
                .strip()
                .lower(),

            "password_hash":
                hash_password(
                    str(
                        row[
                            "password"
                        ]
                    )
                ),

            "role":
                row[
                    "role"
                ],

            "is_active":
                as_bool(
                    row.get(
                        "is_active"
                    ),
                    True,
                ),

            "is_verified":
                as_bool(
                    row.get(
                        "is_verified"
                    ),
                    True,
                ),
        }

        user = build_instance(
            User,
            values,
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "user_key"
            ],
            instance=user,
        )

        context.store(
            "users",
            row[
                "user_key"
            ],
            user,
        )