from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
)


def import_challenge_skills(
    db: Session,
    batch,
    rows,
    context,
):

    ChallengeSkill = (
        model_for_table(
            "challenge_skills"
        )
    )

    for row in rows:

        challenge = context.get(
            "challenges",
            row[
                "challenge_key"
            ],
        )

        skill = context.get(
            "skills",
            row[
                "skill_key"
            ],
        )

        values = {
            "challenge_id":
                challenge.id,

            "skill_id":
                skill.id,

            "minimum_level":
                row.get(
                    "minimum_level"
                ),

            "required":
                True,
        }

        item = build_instance(
            ChallengeSkill,
            values,
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "challenge_skill_key"
            ],
            instance=item,
        )

        context.store(
            "challenge_skills",
            row[
                "challenge_skill_key"
            ],
            item,
        )