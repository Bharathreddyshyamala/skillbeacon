from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
)


def import_skills(
    db: Session,
    batch,
    rows,
    context,
):

    Skill = model_for_table(
        "skills"
    )

    for row in rows:

        name = str(
            row[
                "name"
            ]
        ).strip()

        existing = db.scalar(
            select(
                Skill
            )
            .where(
                func.lower(
                    Skill.name
                )
                ==
                name.lower()
            )
        )

        if existing:

            context.store(
                "skills",
                row[
                    "skill_key"
                ],
                existing,
            )

            continue

        values = {
            "name":
                name,

            "description":
                row.get(
                    "description"
                ),

            "category":
                row.get(
                    "category"
                ),

            "is_active":
                True,
        }

        skill = build_instance(
            Skill,
            values,
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "skill_key"
            ],
            instance=skill,
        )

        context.store(
            "skills",
            row[
                "skill_key"
            ],
            skill,
        )