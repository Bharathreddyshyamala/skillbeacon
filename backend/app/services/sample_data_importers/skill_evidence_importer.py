from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
    set_first_existing,
)


def import_skill_evidence(
    db: Session,
    batch,
    rows,
    context,
):

    Evidence = model_for_table(
        "skill_evidence"
    )

    for row in rows:

        user_skill = context.get(
            "user_skills",
            row[
                "user_skill_key"
            ],
        )

        values = {
            "user_skill_id":
                user_skill.id,

            "title":
                row.get(
                    "title"
                ),

            "description":
                row.get(
                    "description"
                ),

            "score":
                row.get(
                    "score"
                ),
        }

        set_first_existing(
            Evidence,
            values,
            [
                "evidence_type",
                "type",
            ],
            row.get(
                "evidence_type"
            ),
            required=False,
        )

        set_first_existing(
            Evidence,
            values,
            [
                "url",
                "evidence_url",
            ],
            row.get(
                "url"
            ),
            required=False,
        )

        evidence = build_instance(
            Evidence,
            values,
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "evidence_key"
            ],
            instance=evidence,
        )

        context.store(
            "skill_evidence",
            row[
                "evidence_key"
            ],
            evidence,
        )