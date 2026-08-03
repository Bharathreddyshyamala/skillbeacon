from typing import (
    Optional,
    Tuple,
)

from uuid import UUID

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.application import (
    Application,
    ApplicationStatus,
)


def application_load_options():

    return (
        selectinload(
            Application.opportunity
        ),

        selectinload(
            Application.student
        ),
    )


# ============================================================
# Create
# ============================================================


def create_application(
    db: Session,
    opportunity_id: UUID,
    student_id: UUID,
    cover_letter: Optional[str],
    resume_path: Optional[str],
    profile_snapshot: dict,
):

    application = Application(
        opportunity_id=opportunity_id,
        student_id=student_id,
        status=(
            ApplicationStatus.SUBMITTED
        ),
        cover_letter=cover_letter,
        resume_path=resume_path,
        profile_snapshot=profile_snapshot,
    )

    db.add(application)

    db.flush()

    return application


# ============================================================
# Get by ID
# ============================================================


def get_application_by_id(
    db: Session,
    application_id: UUID,
):

    statement = (
        select(Application)
        .options(
            *application_load_options()
        )
        .where(
            Application.id
            == application_id
        )
    )

    return db.scalar(statement)


# ============================================================
# Duplicate check
# ============================================================


def get_existing_application(
    db: Session,
    opportunity_id: UUID,
    student_id: UUID,
):

    statement = (
        select(Application)
        .where(
            Application.opportunity_id
            == opportunity_id,
            Application.student_id
            == student_id,
        )
    )

    return db.scalar(statement)


# ============================================================
# Student-owned application
# ============================================================


def get_application_for_student(
    db: Session,
    application_id: UUID,
    student_id: UUID,
):

    statement = (
        select(Application)
        .options(
            *application_load_options()
        )
        .where(
            Application.id
            == application_id,
            Application.student_id
            == student_id,
        )
    )

    return db.scalar(statement)


# ============================================================
# Student applications
# ============================================================


def list_student_applications(
    db: Session,
    student_id: UUID,
    status_filter: Optional[
        ApplicationStatus
    ] = None,
    opportunity_id: Optional[
        UUID
    ] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[list, int]:

    filters = [
        Application.student_id
        == student_id
    ]

    if status_filter:
        filters.append(
            Application.status
            == status_filter
        )

    if opportunity_id:
        filters.append(
            Application.opportunity_id
            == opportunity_id
        )


    count_statement = (
        select(
            func.count(
                Application.id
            )
        )
        .where(
            *filters
        )
    )

    total = (
        db.scalar(
            count_statement
        )
        or 0
    )


    statement = (
        select(Application)
        .options(
            *application_load_options()
        )
        .where(
            *filters
        )
        .order_by(
            Application.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )


    items = list(
        db.scalars(
            statement
        )
    )


    return items, total


# ============================================================
# Opportunity applicants
# ============================================================


def list_opportunity_applications(
    db: Session,
    opportunity_id: UUID,
    status_filter: Optional[
        ApplicationStatus
    ] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[list, int]:

    filters = [
        Application.opportunity_id
        == opportunity_id
    ]


    if status_filter:

        filters.append(
            Application.status
            == status_filter
        )


    count_statement = (
        select(
            func.count(
                Application.id
            )
        )
        .where(
            *filters
        )
    )


    total = (
        db.scalar(
            count_statement
        )
        or 0
    )


    statement = (
        select(Application)
        .options(
            *application_load_options()
        )
        .where(
            *filters
        )
        .order_by(
            Application.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )


    items = list(
        db.scalars(
            statement
        )
    )


    return items, total


# ============================================================
# Status
# ============================================================


def update_application_status(
    application: Application,
    new_status: ApplicationStatus,
):

    application.status = (
        new_status
    )


# ============================================================
# Withdraw
# ============================================================


def withdraw_application(
    application: Application,
):

    application.status = (
        ApplicationStatus.WITHDRAWN
    )


# ============================================================
# Employer note
# ============================================================


def update_application_note(
    application: Application,
    note: Optional[str],
):

    application.employer_note = note