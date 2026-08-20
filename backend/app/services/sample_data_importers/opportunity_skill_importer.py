from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
)


def import_opportunity_skills(
    db: Session,
    batch,
    rows,
    context,
):

    OpportunitySkill = (
        model_for_table(
            "opportunity_skills"
        )
    )

    for row in rows:

        opportunity = context.get(
            "opportunities",
            row[
                "opportunity_key"
            ],
        )

        skill = context.get(
            "skills",
            row[
                "skill_key"
            ],
        )

        values = {
            "opportunity_id":
                opportunity.id,

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
            OpportunitySkill,
            values,
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "opportunity_skill_key"
            ],
            instance=item,
        )

        context.store(
            "opportunity_skills",
            row[
                "opportunity_skill_key"
            ],
            item,
        )