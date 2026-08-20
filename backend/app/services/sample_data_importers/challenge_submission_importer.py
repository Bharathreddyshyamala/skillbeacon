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


def import_challenge_submissions(
    db: Session,
    batch,
    rows,
    context,
):

    Submission = (
        model_for_table(
            "challenge_submissions"
        )
    )

    for row in rows:

        challenge = context.get(
            "challenges",
            row[
                "challenge_key"
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

        values = {
            "challenge_id":
                challenge.id,

            "student_id":
                student.id,

            "submission_text":
                row.get(
                    "submission_text"
                ),

            "repository_url":
                row.get(
                    "repository_url"
                ),

            "demo_url":
                row.get(
                    "demo_url"
                ),

            "status":
                row.get(
                    "status"
                ),

            "score":
                row.get(
                    "score"
                ),

            "employer_feedback":
                row.get(
                    "employer_feedback"
                ),

            "profile_snapshot":
                build_profile_snapshot(
                    db,
                    student,
                    profile,
                ),
        }

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
                Submission,
                values,
                [
                    "reviewed_at",
                ],
                datetime.now(
                    timezone.utc
                ),
                required=False,
            )

        submission = (
            build_instance(
                Submission,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "submission_key"
            ],
            instance=submission,
        )

        context.store(
            "challenge_submissions",
            row[
                "submission_key"
            ],
            submission,
        )