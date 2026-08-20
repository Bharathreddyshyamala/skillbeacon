from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
)


def import_challenges(
    db: Session,
    batch,
    rows,
    context,
):

    Challenge = (
        model_for_table(
            "challenges"
        )
    )

    for row in rows:

        employer = context.get(
            "users",
            row[
                "employer_user_key"
            ],
        )

        values = {
            "employer_id":
                employer.id,

            "title":
                row.get(
                    "title"
                ),

            "company_name":
                row.get(
                    "company_name"
                ),

            "description":
                row.get(
                    "description"
                ),

            "instructions":
                row.get(
                    "instructions"
                ),

            "deliverables":
                row.get(
                    "deliverables"
                ),

            "challenge_type":
                row.get(
                    "challenge_type"
                ),

            "difficulty":
                row.get(
                    "difficulty"
                ),

            "status":
                row.get(
                    "status"
                ),

            "deadline":
                row.get(
                    "deadline"
                ),
        }

        challenge = (
            build_instance(
                Challenge,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "challenge_key"
            ],
            instance=challenge,
        )

        context.store(
            "challenges",
            row[
                "challenge_key"
            ],
            challenge,
        )