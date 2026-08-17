from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    has_column,
    model_for_table,
    set_first_existing,
    coerce_value,
)


def import_skill_verifications(
    db: Session,
    batch,
    rows,
    context,
):

    Verification = model_for_table(
        "skill_verifications"
    )

    Evidence = model_for_table(
        "skill_evidence"
    )

    for row in rows:

        evidence = context.get(
            "skill_evidence",
            row[
                "evidence_key"
            ],
        )

        verifier = context.get(
            "users",
            row[
                "verifier_user_key"
            ],
        )

        values = {}

        set_first_existing(
            Verification,
            values,
            [
                "evidence_id",
                "skill_evidence_id",
            ],
            evidence.id,
        )

        set_first_existing(
            Verification,
            values,
            [
                "verifier_id",
                "verified_by_user_id",
                "mentor_id",
            ],
            verifier.id,
        )

        set_first_existing(
            Verification,
            values,
            [
                "status",
            ],
            row.get(
                "status"
            ),
        )

        set_first_existing(
            Verification,
            values,
            [
                "comments",
                "note",
                "feedback",
            ],
            row.get(
                "note"
            ),
            required=False,
        )

        verification = (
            build_instance(
                Verification,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "verification_key"
            ],
            instance=verification,
        )

        context.store(
            "skill_verifications",
            row[
                "verification_key"
            ],
            verification,
        )

        if has_column(
            Evidence,
            "status",
        ):

            evidence.status = (
                coerce_value(
                    Evidence,
                    "status",
                    row.get(
                        "status"
                    ),
                )
            )