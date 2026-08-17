from sqlalchemy.orm import Session

from app.models.user import UserRole

from app.services.sample_data.helpers import (
    add_and_track,
    build_instance,
    enum_text,
    has_column,
)


def _get_profile_model(
    user,
):
    role = (
        enum_text(
            user.role
        )
        or ""
    ).lower()

    relationships = (
        user.__class__
        .__mapper__
        .relationships
    )

    if role == "student":
        relationship_candidates = [
            "student_profile",
            "profile",
        ]

    elif role == "employer":
        relationship_candidates = [
            "employer_profile",
            "profile",
        ]

    elif role == "mentor":
        relationship_candidates = [
            "mentor_profile",
            "profile",
        ]

    else:
        raise ValueError(
            (
                "Unsupported user role "
                f"for profile import: "
                f"{role}"
            )
        )

    for relationship_name in (
        relationship_candidates
    ):
        if (
            relationship_name
            in relationships
        ):
            relationship = (
                relationships[
                    relationship_name
                ]
            )

            return (
                relationship
                .mapper
                .class_
            )

    raise RuntimeError(
        (
            "Could not determine profile "
            f"model for role '{role}'. "
            "Check the relationships "
            "defined in User."
        )
    )


def _set_if_exists(
    model,
    values,
    field_name,
    value,
):
    if (
        value is not None
        and value != ""
        and has_column(
            model,
            field_name,
        )
    ):
        values[
            field_name
        ] = value


def import_profiles(
    db: Session,
    batch,
    rows,
    context,
):
    for row in rows:

        user = context.get(
            "users",
            row[
                "user_key"
            ],
        )

        ProfileModel = (
            _get_profile_model(
                user
            )
        )

        values = {
            "user_id":
                user.id,
        }

        first_name = (
            row.get(
                "first_name"
            )
        )

        last_name = (
            row.get(
                "last_name"
            )
        )

        headline = (
            row.get(
                "headline"
            )
        )

        summary = (
            row.get(
                "summary"
            )
        )

        education = (
            row.get(
                "education"
            )
        )

        work_experience = (
            row.get(
                "work_experience"
            )
        )

        company_name = (
            row.get(
                "company_name"
            )
        )

        company_website = (
            row.get(
                "company_website"
            )
        )

        mentor_bio = (
            row.get(
                "mentor_bio"
            )
        )

        _set_if_exists(
            ProfileModel,
            values,
            "first_name",
            first_name,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "last_name",
            last_name,
        )

        full_name = (
            f"{first_name or ''} "
            f"{last_name or ''}"
        ).strip()

        _set_if_exists(
            ProfileModel,
            values,
            "full_name",
            full_name,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "headline",
            headline,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "professional_title",
            headline,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "summary",
            summary,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "bio",
            summary,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "education",
            education,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "work_experience",
            work_experience,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "company_name",
            company_name,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "company_website",
            company_website,
        )

        _set_if_exists(
            ProfileModel,
            values,
            "mentor_bio",
            mentor_bio,
        )

        if (
            mentor_bio
            and not summary
        ):
            _set_if_exists(
                ProfileModel,
                values,
                "bio",
                mentor_bio,
            )

            _set_if_exists(
                ProfileModel,
                values,
                "summary",
                mentor_bio,
            )

        profile = (
            build_instance(
                ProfileModel,
                values,
            )
        )

        add_and_track(
            db=db,
            batch_id=batch.id,
            logical_key=row[
                "user_key"
            ],
            instance=profile,
        )

        context.store(
            "profiles",
            row[
                "user_key"
            ],
            profile,
        )