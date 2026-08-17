from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    as_bool,
    build_instance,
    model_for_table,
    set_first_existing,
)


def import_notifications(
    db: Session,
    batch,
    rows,
    context,
):

    Notification = (
        model_for_table(
            "notifications"
        )
    )

    related_maps = {
        "application":
            "applications",

        "mentorship":
            "mentorships",

        "challenge":
            "challenges",

        "challenge_submission":
            "challenge_submissions",

        "verification":
            "skill_verifications",
    }

    for row in rows:

        user = context.get(
            "users",
            row[
                "user_key"
            ],
        )

        entity_type = row.get(
            "related_entity_type"
        )

        ref_key = row.get(
            "related_ref_key"
        )

        related_id = None

        group = (
            related_maps.get(
                str(entity_type)
            )
            if entity_type
            else None
        )

        if (
            group
            and ref_key
        ):

            related = (
                context.get_optional(
                    group,
                    ref_key,
                )
            )

            if related:
                related_id = (
                    related.id
                )

        values = {
            "user_id":
                user.id,

            "title":
                row.get(
                    "title"
                ),

            "message":
                row.get(
                    "message"
                ),

            "action_url":
                row.get(
                    "action_url"
                ),

            "is_read":
                as_bool(
                    row.get(
                        "is_read"
                    ),
                    False,
                ),

            "related_entity_type":
                entity_type,

            "related_entity_id":
                related_id,
        }

        set_first_existing(
            Notification,
            values,
            [
                "notification_type",
                "type",
            ],
            row.get(
                "notification_type"
            ),
            required=False,
        )

        notification = (
            build_instance(
                Notification,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "notification_key"
            ],
            instance=notification,
        )

        context.store(
            "notifications",
            row[
                "notification_key"
            ],
            notification,
        )