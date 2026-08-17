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

from app.services.sample_data.snapshot import (
    build_profile_snapshot,
)


def import_applications(
    db: Session,
    batch,
    rows,
    context,
):

    Application = (
        model_for_table(
            "applications"
        )
    )

    for row in rows:

        opportunity = context.get(
            "opportunities",
            row[
                "opportunity_key"
            ],
        )

        student = context.get(
            "users",
            row[
                "student_user_key"
            ],
        )

        profile = context.get(
            "profiles",
            row[
                "student_user_key"
            ],
        )

        resume = (
            context.get_optional(
                "resume_files",
                row.get(
                    "resume_key"
                ),
            )
        )

        object_key = (
            resume[
                "object_key"
            ]
            if resume
            else None
        )

        values = {
            "opportunity_id":
                opportunity.id,

            "student_id":
                student.id,

            "status":
                row.get(
                    "status"
                ),

            "cover_letter":
                row.get(
                    "cover_letter"
                ),

            "employer_note":
                row.get(
                    "employer_note"
                ),

            "profile_snapshot":
                build_profile_snapshot(
                    db,
                    student,
                    profile,
                ),
        }

        set_first_existing(
            Application,
            values,
            [
                "resume_object_key",
                "resume_key",
                "resume_path",
            ],
            object_key,
            required=False,
        )

        if (
            str(
                row.get(
                    "status",
                    "",
                )
            ).lower()
            != "submitted"
        ):

            set_first_existing(
                Application,
                values,
                [
                    "reviewed_at",
                ],
                datetime.now(
                    timezone.utc
                ),
                required=False,
            )

        application = (
            build_instance(
                Application,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "application_key"
            ],
            instance=application,
        )

        context.store(
            "applications",
            row[
                "application_key"
            ],
            application,
        )