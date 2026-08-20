from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
)


def import_user_skills(
    db: Session,
    batch,
    rows,
    context,
):

    UserSkill = model_for_table(
        "user_skills"
    )

    for row in rows:

        user = context.get(
            "users",
            row[
                "user_key"
            ],
        )

        skill = context.get(
            "skills",
            row[
                "skill_key"
            ],
        )

        values = {
            "user_id":
                user.id,

            "skill_id":
                skill.id,

            "level":
                row.get(
                    "level"
                ),

            "confidence_score":
                row.get(
                    "confidence_score"
                ),
        }

        user_skill = (
            build_instance(
                UserSkill,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "user_skill_key"
            ],
            instance=user_skill,
        )

        context.store(
            "user_skills",
            row[
                "user_skill_key"
            ],
            user_skill,
        )