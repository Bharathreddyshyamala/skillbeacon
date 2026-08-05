from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from typing import (
    Dict,
    Set,
)

from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.exc import (
    IntegrityError,
)

from sqlalchemy.orm import Session

from app.models.application import (
    ApplicationStatus,
)

from app.models.opportunity import (
    OpportunityStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.application_repository import (
    create_application,
    get_application_by_id,
    get_application_for_student,
    get_existing_application,
    list_opportunity_applications,
    list_student_applications,
    update_application_note,
    update_application_status,
    withdraw_application,
)

from app.repositories.opportunity_repository import (
    get_opportunity,
)

from app.repositories.skill_repository import (
    list_user_skills,
)

from app.schemas.application_schema import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationStatusRequest,
)




VALID_EMPLOYER_TRANSITIONS = {

    ApplicationStatus.SUBMITTED: {
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.REJECTED,
    },

    ApplicationStatus.UNDER_REVIEW: {
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.REJECTED,
    },

    ApplicationStatus.SHORTLISTED: {
        ApplicationStatus.ACCEPTED,
        ApplicationStatus.REJECTED,
    },
}


TERMINAL_STATUSES: Set[
    ApplicationStatus
] = {
    ApplicationStatus.ACCEPTED,
    ApplicationStatus.REJECTED,
    ApplicationStatus.WITHDRAWN,
}




def ensure_student(
    current_user: User,
):

    if (
        current_user.role
        != UserRole.STUDENT
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Only students can submit "
                "applications."
            ),
        )


def ensure_application_manager(
    current_user: User,
):

    allowed_roles = {
        UserRole.EMPLOYER,
        UserRole.ADMIN,
    }

    if (
        current_user.role
        not in allowed_roles
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Only employers or admins "
                "can manage applications."
            ),
        )


def ensure_employer_owns_opportunity(
    current_user: User,
    opportunity,
):

    if (
        current_user.role
        == UserRole.ADMIN
    ):
        return

    if (
        opportunity.employer_id
        != current_user.id
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "You cannot manage applications "
                "for another employer's "
                "opportunity."
            ),
        )




def create_profile_snapshot(
    db: Session,
    current_user: User,
):


    profile = getattr(
        current_user,
        "student_profile",
        None,
    )


    if not profile:

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Complete your student profile "
                "before applying."
            ),
        )


    user_skills = list_user_skills(
        db,
        current_user.id,
    )


    skill_snapshot = []

    for user_skill in user_skills:

        skill_snapshot.append(
            {
                "name":
                    user_skill.skill.name,

                "level":
                    (
                        user_skill.level.value
                        if hasattr(
                            user_skill.level,
                            "value",
                        )
                        else user_skill.level
                    ),

                "confidence_score":
                    user_skill.confidence_score,
            }
        )


    snapshot = {
        "first_name":
            getattr(
                profile,
                "first_name",
                None,
            ),

        "last_name":
            getattr(
                profile,
                "last_name",
                None,
            ),

        "headline":
            getattr(
                profile,
                "headline",
                None,
            ),

        "summary":
            getattr(
                profile,
                "summary",
                None,
            ),

        "education":
            getattr(
                profile,
                "education",
                None,
            ),

        "work_experience":
            getattr(
                profile,
                "work_experience",
                None,
            ),

        "skills":
            skill_snapshot,
    }


    resume_path = getattr(
        profile,
        "resume_path",
        None,
    )


    return snapshot, resume_path




def student_application_response(
    application,
):

    opportunity = (
        application.opportunity
    )

    return {
        "id":
            application.id,

        "opportunity_id":
            application.opportunity_id,

        "opportunity_title":
            opportunity.title,

        "company_name":
            opportunity.company_name,

        "opportunity_type":
            opportunity.opportunity_type,

        "status":
            application.status,

        "cover_letter":
            application.cover_letter,

        "resume_available":
            bool(
                application.resume_path
            ),

        "created_at":
            application.created_at,

        "updated_at":
            application.updated_at,
    }




def employer_application_response(
    application,
):

    snapshot = (
        application.profile_snapshot
        or {}
    )

    first_name = (
        snapshot.get(
            "first_name"
        )
        or ""
    )

    last_name = (
        snapshot.get(
            "last_name"
        )
        or ""
    )

    student_name = (
        f"{first_name} {last_name}"
        .strip()
    )

    if not student_name:
        student_name = (
            application.student.email
        )


    return {
        "id":
            application.id,

        "opportunity_id":
            application.opportunity_id,

        "student_id":
            application.student_id,

        "student_email":
            application.student.email,

        "student_name":
            student_name,

        "status":
            application.status,

        "cover_letter":
            application.cover_letter,

        "profile_snapshot":
            snapshot,

        "resume_available":
            bool(
                application.resume_path
            ),

        "employer_note":
            application.employer_note,

        "reviewed_at":
            application.reviewed_at,

        "created_at":
            application.created_at,

        "updated_at":
            application.updated_at,
    }




def submit_application(
    db: Session,
    current_user: User,
    request: ApplicationCreateRequest,
):

    ensure_student(
        current_user
    )


    opportunity = get_opportunity(
        db,
        request.opportunity_id,
    )


    if not opportunity:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Opportunity not found."
            ),
        )


    if (
        opportunity.status
        != OpportunityStatus.OPEN.value
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This opportunity is not open."
            ),
        )


    today = (
        datetime.now(
            timezone.utc
        ).date()
    )


    if (
        opportunity.deadline
        and opportunity.deadline
        < today
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "The application deadline "
                "has passed."
            ),
        )


    existing = get_existing_application(
        db,
        opportunity.id,
        current_user.id,
    )


    if existing:

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "You already applied to "
                "this opportunity."
            ),
        )


    (
        profile_snapshot,
        resume_path,
    ) = create_profile_snapshot(
        db,
        current_user,
    )


    application = create_application(
        db=db,

        opportunity_id=(
            opportunity.id
        ),

        student_id=(
            current_user.id
        ),

        cover_letter=(
            request.cover_letter.strip()
            if request.cover_letter
            else None
        ),

        resume_path=resume_path,

        profile_snapshot=(
            profile_snapshot
        ),
    )


    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "You already applied to "
                "this opportunity."
            ),
        )


    application = (
        get_application_by_id(
            db,
            application.id,
        )
    )


    return student_application_response(
        application
    )




def get_my_applications(
    db: Session,
    current_user: User,
    status_filter=None,
    opportunity_id=None,
    limit=20,
    offset=0,
):

    ensure_student(
        current_user
    )


    items, total = (
        list_student_applications(
            db=db,

            student_id=(
                current_user.id
            ),

            status_filter=(
                status_filter
            ),

            opportunity_id=(
                opportunity_id
            ),

            limit=limit,

            offset=offset,
        )
    )


    return {
        "items": [
            student_application_response(
                item
            )
            for item in items
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }




def get_my_application(
    db: Session,
    current_user: User,
    application_id: UUID,
):

    ensure_student(
        current_user
    )


    application = (
        get_application_for_student(
            db,
            application_id,
            current_user.id,
        )
    )


    if not application:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Application not found."
            ),
        )


    return student_application_response(
        application
    )




def withdraw_my_application(
    db: Session,
    current_user: User,
    application_id: UUID,
):

    ensure_student(
        current_user
    )


    application = (
        get_application_for_student(
            db,
            application_id,
            current_user.id,
        )
    )


    if not application:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Application not found."
            ),
        )


    if (
        application.status
        in TERMINAL_STATUSES
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This application can no "
                "longer be withdrawn."
            ),
        )


    withdraw_application(
        application
    )


    db.commit()


    application = (
        get_application_by_id(
            db,
            application.id,
        )
    )


    return student_application_response(
        application
    )




def get_opportunity_applications(
    db: Session,
    current_user: User,
    opportunity_id: UUID,
    status_filter=None,
    limit=20,
    offset=0,
):

    ensure_application_manager(
        current_user
    )


    opportunity = get_opportunity(
        db,
        opportunity_id,
    )


    if not opportunity:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Opportunity not found."
            ),
        )


    ensure_employer_owns_opportunity(
        current_user,
        opportunity,
    )


    items, total = (
        list_opportunity_applications(
            db=db,

            opportunity_id=(
                opportunity.id
            ),

            status_filter=(
                status_filter
            ),

            limit=limit,

            offset=offset,
        )
    )


    return {
        "items": [
            employer_application_response(
                item
            )
            for item in items
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }




def validate_employer_transition(
    current_status,
    new_status,
):

    if (
        current_status
        in TERMINAL_STATUSES
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This application is in "
                "a terminal state."
            ),
        )


    allowed = (
        VALID_EMPLOYER_TRANSITIONS
        .get(
            current_status,
            set(),
        )
    )


    if new_status not in allowed:

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                f"Cannot change application "
                f"from {current_status.value} "
                f"to {new_status.value}."
            ),
        )




def change_application_status(
    db: Session,
    current_user: User,
    application_id: UUID,
    request: ApplicationStatusRequest,
):

    ensure_application_manager(
        current_user
    )


    application = (
        get_application_by_id(
            db,
            application_id,
        )
    )


    if not application:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Application not found."
            ),
        )


    ensure_employer_owns_opportunity(
        current_user,
        application.opportunity,
    )


    validate_employer_transition(
        application.status,
        request.status,
    )


    update_application_status(
        application,
        request.status,
    )


    if (
        request.employer_note
        is not None
    ):

        update_application_note(
            application,
            request.employer_note,
        )


    application.reviewed_at = (
        datetime.now(
            timezone.utc
        )
    )


    db.commit()


    application = (
        get_application_by_id(
            db,
            application.id,
        )
    )


    return employer_application_response(
        application
    )




def change_application_note(
    db: Session,
    current_user: User,
    application_id: UUID,
    request: ApplicationNoteRequest,
):

    ensure_application_manager(
        current_user
    )


    application = (
        get_application_by_id(
            db,
            application_id,
        )
    )


    if not application:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Application not found."
            ),
        )


    ensure_employer_owns_opportunity(
        current_user,
        application.opportunity,
    )


    update_application_note(
        application,
        request.employer_note,
    )


    db.commit()


    application = (
        get_application_by_id(
            db,
            application.id,
        )
    )


    return employer_application_response(
        application
    )




def get_application_resume(
    db: Session,
    current_user: User,
    application_id: UUID,
):

    application = (
        get_application_by_id(
            db,
            application_id,
        )
    )


    if not application:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Application not found.",
        )


    allowed = False


    if (
        current_user.role
        == UserRole.STUDENT
        and application.student_id
        == current_user.id
    ):

        allowed = True


    elif (
        current_user.role
        == UserRole.EMPLOYER
        and application.opportunity.employer_id
        == current_user.id
    ):

        allowed = True


    elif (
        current_user.role
        == UserRole.ADMIN
    ):

        allowed = True


    if not allowed:

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "You cannot access this résumé."
            ),
        )


    if not application.resume_path:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "No résumé was attached "
                "to this application."
            ),
        )


    file_path = Path(
        application.resume_path
    )


    if (
        not file_path.exists()
        or not file_path.is_file()
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Résumé file not found."
            ),
        )


    return file_path