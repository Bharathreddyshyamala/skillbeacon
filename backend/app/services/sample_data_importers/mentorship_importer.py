from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
    set_first_existing,
)


def import_mentorships(
    db: Session,
    batch,
    rows,
    context,
):

    Mentorship = (
        model_for_table(
            "mentorships"
        )
    )

    for row in rows:

        student = context.get(
            "users",
            row[
                "student_user_key"
            ],
        )

        mentor = context.get(
            "users",
            row[
                "mentor_user_key"
            ],
        )

        values = {
            "student_id":
                student.id,

            "mentor_id":
                mentor.id,

            "focus_area":
                (
                    row.get(
                        "focus_area"
                    )
                    or
                    "Career development"
                ),

            "message":
                row.get(
                    "message"
                ),

            "goals":
                row.get(
                    "goals"
                ),

            "status":
                row.get(
                    "status"
                ),
        }

        status_value = str(
            row.get(
                "status",
                "",
            )
        ).lower()

        if status_value in {
            "active",
            "completed",
        }:

            set_first_existing(
                Mentorship,
                values,
                [
                    "accepted_at",
                ],
                datetime.now(
                    timezone.utc
                ),
                required=False,
            )

        if (
            status_value
            == "completed"
        ):

            set_first_existing(
                Mentorship,
                values,
                [
                    "completed_at",
                ],
                datetime.now(
                    timezone.utc
                ),
                required=False,
            )

        mentorship = (
            build_instance(
                Mentorship,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "mentorship_key"
            ],
            instance=mentorship,
        )

        context.store(
            "mentorships",
            row[
                "mentorship_key"
            ],
            mentorship,
        )