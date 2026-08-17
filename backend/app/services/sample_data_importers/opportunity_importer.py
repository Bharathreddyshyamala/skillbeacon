from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    model_for_table,
    set_first_existing,
)


def import_opportunities(
    db: Session,
    batch,
    rows,
    context,
):

    Opportunity = (
        model_for_table(
            "opportunities"
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

            "location":
                row.get(
                    "location"
                ),

            "work_mode":
                row.get(
                    "work_mode"
                ),

            "opportunity_type":
                row.get(
                    "opportunity_type"
                ),

            "salary_min":
                row.get(
                    "salary_min"
                ),

            "salary_max":
                row.get(
                    "salary_max"
                ),

            "currency":
                row.get(
                    "currency"
                ),

            "deadline":
                row.get(
                    "deadline"
                ),

            "status":
                row.get(
                    "status"
                ),
        }

        set_first_existing(
            Opportunity,
            values,
            [
                "application_url",
                "external_url",
            ],
            row.get(
                "external_url"
            ),
            required=False,
        )

        opportunity = (
            build_instance(
                Opportunity,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "opportunity_key"
            ],
            instance=opportunity,
        )

        context.store(
            "opportunities",
            row[
                "opportunity_key"
            ],
            opportunity,
        )