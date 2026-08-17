from datetime import timedelta

from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    ensure_datetime,
    model_for_table,
)


def import_mentorship_sessions(
    db: Session,
    batch,
    rows,
    context,
):

    SessionModel = (
        model_for_table(
            "mentorship_sessions"
        )
    )

    for row in rows:

        mentorship = context.get(
            "mentorships",
            row[
                "mentorship_key"
            ],
        )

        start = ensure_datetime(
            row.get(
                "scheduled_at"
            )
        )

        duration = int(
            row.get(
                "duration_minutes"
            )
            or 60
        )

        end = (
            start
            + timedelta(
                minutes=duration
            )
            if start
            else None
        )

        values = {
            "mentorship_id":
                mentorship.id,

            "created_by_id":
                mentorship.mentor_id,

            "title":
                row.get(
                    "title"
                ),

            "description":
                row.get(
                    "notes"
                ),

            "scheduled_start":
                start,

            "scheduled_end":
                end,

            "meeting_url":
                row.get(
                    "meeting_url"
                ),

            "shared_notes":
                row.get(
                    "notes"
                ),

            "status":
                row.get(
                    "status"
                ),

            "scheduled_at":
                start,

            "duration_minutes":
                duration,

            "notes":
                row.get(
                    "notes"
                ),
        }

        session = build_instance(
            SessionModel,
            values,
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "session_key"
            ],
            instance=session,
        )

        context.store(
            "mentorship_sessions",
            row[
                "session_key"
            ],
            session,
        )