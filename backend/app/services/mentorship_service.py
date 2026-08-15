from datetime import (
    datetime,
    timezone,
)

from typing import Optional
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.exc import (
    IntegrityError,
)

from sqlalchemy.orm import Session

from app.models.mentorship import (
    MentorshipSessionStatus,
    MentorshipStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.mentorship_repository import (
    create_mentorship,
    create_mentorship_session,
    get_active_mentorship_for_pair,
    get_mentorship_by_id,
    get_mentorship_session_by_id,
    get_user_by_id,
    list_mentor_skills,
    list_mentors,
    list_user_mentorships,
)

from app.schemas.mentorship_schema import (
    MentorshipCreateRequest,
    MentorshipDecision,
    MentorshipRespondRequest,
    MentorshipSessionCreateRequest,
    MentorshipSessionStatusRequest,
    SessionStatusUpdate,
)

from app.services.notification_service import (
    create_notification,
)




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
                "Only students can perform "
                "this action."
            ),
        )


def ensure_mentor(
    current_user: User,
):

    if (
        current_user.role
        not in {
            UserRole.MENTOR,
            UserRole.ADMIN,
        }
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Only mentors or admins "
                "can perform this action."
            ),
        )


def ensure_mentor_owns_mentorship(
    current_user: User,
    mentorship,
):

    if (
        current_user.role
        == UserRole.ADMIN
    ):
        return

    if (
        mentorship.mentor_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "You cannot manage another "
                "mentor's mentorship."
            ),
        )


def ensure_participant(
    current_user: User,
    mentorship,
):

    if (
        current_user.role
        == UserRole.ADMIN
    ):
        return

    participant_ids = {
        mentorship.student_id,
        mentorship.mentor_id,
    }

    if (
        current_user.id
        not in participant_ids
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "You are not a participant "
                "in this mentorship."
            ),
        )




def get_user_profile(
    user: User,
):


    return (
        getattr(
            user,
            "mentor_profile",
            None,
        )
        or getattr(
            user,
            "student_profile",
            None,
        )
        or getattr(
            user,
            "profile",
            None,
        )
    )


def get_user_display_name(
    user: User,
):

    profile = get_user_profile(
        user
    )

    if profile:

        full_name = getattr(
            profile,
            "full_name",
            None,
        )

        if full_name:
            return str(
                full_name
            )

        first_name = getattr(
            profile,
            "first_name",
            None,
        )

        last_name = getattr(
            profile,
            "last_name",
            None,
        )

        name = " ".join(
            value
            for value in [
                first_name,
                last_name,
            ]
            if value
        ).strip()

        if name:
            return name

    return user.email


def get_optional_profile_value(
    user: User,
    *field_names,
):

    profile = get_user_profile(
        user
    )

    if not profile:
        return None

    for field_name in field_names:

        value = getattr(
            profile,
            field_name,
            None,
        )

        if value not in (
            None,
            "",
            [],
        ):

            if isinstance(
                value,
                list,
            ):
                return ", ".join(
                    str(item)
                    for item in value
                )

            return value

    return None




def session_response(
    session,
):

    return {
        "id":
            session.id,

        "mentorship_id":
            session.mentorship_id,

        "created_by_id":
            session.created_by_id,

        "title":
            session.title,

        "description":
            session.description,

        "scheduled_start":
            session.scheduled_start,

        "scheduled_end":
            session.scheduled_end,

        "meeting_url":
            session.meeting_url,

        "shared_notes":
            session.shared_notes,

        "status":
            session.status,

        "created_at":
            session.created_at,

        "updated_at":
            session.updated_at,
    }


def mentorship_response(
    mentorship,
):

    return {
        "id":
            mentorship.id,

        "student_id":
            mentorship.student_id,

        "student_name":
            get_user_display_name(
                mentorship.student
            ),

        "student_email":
            mentorship.student.email,

        "mentor_id":
            mentorship.mentor_id,

        "mentor_name":
            get_user_display_name(
                mentorship.mentor
            ),

        "mentor_email":
            mentorship.mentor.email,

        "focus_area":
            mentorship.focus_area,

        "goals":
            mentorship.goals,

        "message":
            mentorship.message,

        "mentor_response":
            mentorship.mentor_response,

        "status":
            mentorship.status,

        "accepted_at":
            mentorship.accepted_at,

        "completed_at":
            mentorship.completed_at,

        "created_at":
            mentorship.created_at,

        "updated_at":
            mentorship.updated_at,

        "sessions": [
            session_response(
                session
            )
            for session
            in mentorship.sessions
        ],
    }




def browse_mentors(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    skill_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0,
):

    ensure_student(
        current_user
    )

    mentors, total = list_mentors(
        db=db,
        search=search,
        skill_id=skill_id,
        limit=limit,
        offset=offset,
    )

    items = []

    for mentor in mentors:

        user_skills = (
            list_mentor_skills(
                db,
                mentor.id,
            )
        )

        skills = []

        for user_skill in user_skills:

            level = (
                user_skill.level.value
                if hasattr(
                    user_skill.level,
                    "value",
                )
                else user_skill.level
            )

            skills.append(
                {
                    "id":
                        user_skill.skill_id,

                    "name":
                        user_skill.skill.name,

                    "level":
                        level,

                    "confidence_score":
                        user_skill.confidence_score,
                }
            )

        years_experience = (
            get_optional_profile_value(
                mentor,
                "years_experience",
            )
        )

        if years_experience is not None:

            try:
                years_experience = int(
                    years_experience
                )

            except (
                TypeError,
                ValueError,
            ):
                years_experience = None

        items.append(
            {
                "mentor_id":
                    mentor.id,

                "email":
                    mentor.email,

                "name":
                    get_user_display_name(
                        mentor
                    ),

                "headline":
                    get_optional_profile_value(
                        mentor,
                        "headline",
                        "professional_title",
                    ),

                "bio":
                    get_optional_profile_value(
                        mentor,
                        "bio",
                        "summary",
                    ),

                "expertise":
                    get_optional_profile_value(
                        mentor,
                        "expertise",
                        "specialization",
                        "industry",
                    ),

                "years_experience":
                    years_experience,

                "skills":
                    skills,
            }
        )

    return {
        "items":
            items,

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }




def request_mentorship(
    db: Session,
    current_user: User,
    request: MentorshipCreateRequest,
):

    ensure_student(
        current_user
    )

    mentor = get_user_by_id(
        db,
        request.mentor_id,
    )

    if not mentor:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Mentor not found.",
        )

    if (
        mentor.role
        != UserRole.MENTOR
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "The selected user is not "
                "a mentor."
            ),
        )

    if not mentor.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "This mentor is not currently "
                "available."
            ),
        )

    existing = (
        get_active_mentorship_for_pair(
            db,
            current_user.id,
            mentor.id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "You already have a pending "
                "or active mentorship with "
                "this mentor."
            ),
        )

    mentorship = create_mentorship(
        db=db,
        student_id=current_user.id,
        mentor_id=mentor.id,
        focus_area=(
            request.focus_area.strip()
        ),
        goals=request.goals.strip(),
        message=(
            request.message.strip()
            if request.message
            else None
        ),
    )

    try:

        # Flush first so the mentorship receives its ID
        # before it is referenced by the notification.
        db.flush()


        student_name = get_user_display_name(
            current_user
        )


        create_notification(
            db=db,

            user_id=(
                mentor.id
            ),

            notification_type=(
                "mentorship_request"
            ),

            title=(
                "New mentorship request"
            ),

            message=(
                f"{student_name} sent you "
                f"a mentorship request for "
                f"{request.focus_area.strip()}."
            ),

            action_url=(
                "/app/mentorship"
            ),

            related_entity_type=(
                "mentorship"
            ),

            related_entity_id=(
                mentorship.id
            ),
        )


        # Mentorship request and notification
        # are committed together.
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "You already have a pending "
                "or active mentorship with "
                "this mentor."
            ),
        )

    mentorship = get_mentorship_by_id(
        db,
        mentorship.id,
    )

    return mentorship_response(
        mentorship
    )




def get_my_mentorships(
    db: Session,
    current_user: User,
    status_filter=None,
    limit=20,
    offset=0,
):

    if (
        current_user.role
        == UserRole.STUDENT
    ):
        as_mentor = False

    elif (
        current_user.role
        == UserRole.MENTOR
    ):
        as_mentor = True

    else:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Only students and mentors "
                "can access mentorships."
            ),
        )

    items, total = list_user_mentorships(
        db=db,
        user_id=current_user.id,
        as_mentor=as_mentor,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [
            mentorship_response(
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




def get_mentorship_detail(
    db: Session,
    current_user: User,
    mentorship_id: UUID,
):

    mentorship = get_mentorship_by_id(
        db,
        mentorship_id,
    )

    if not mentorship:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Mentorship not found.",
        )

    ensure_participant(
        current_user,
        mentorship,
    )

    return mentorship_response(
        mentorship
    )




def respond_to_mentorship(
    db: Session,
    current_user: User,
    mentorship_id: UUID,
    request: MentorshipRespondRequest,
):

    ensure_mentor(
        current_user
    )

    mentorship = get_mentorship_by_id(
        db,
        mentorship_id,
    )

    if not mentorship:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Mentorship not found.",
        )

    ensure_mentor_owns_mentorship(
        current_user,
        mentorship,
    )

    if (
        mentorship.status
        != MentorshipStatus.PENDING
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only pending mentorship "
                "requests can be reviewed."
            ),
        )

    mentorship.mentor_response = (
        request.mentor_response.strip()
        if request.mentor_response
        else None
    )

    if (
        request.decision
        == MentorshipDecision.ACCEPTED
    ):

        mentorship.status = (
            MentorshipStatus.ACTIVE
        )

        mentorship.accepted_at = (
            datetime.now(
                timezone.utc
            )
        )


        create_notification(
            db=db,

            user_id=(
                mentorship.student_id
            ),

            notification_type=(
                "mentorship_accepted"
            ),

            title=(
                "Mentorship request accepted"
            ),

            message=(
                f"{get_user_display_name(mentorship.mentor)} "
                f"accepted your mentorship request "
                f"for {mentorship.focus_area}."
            ),

            action_url=(
                "/app/mentorship"
            ),

            related_entity_type=(
                "mentorship"
            ),

            related_entity_id=(
                mentorship.id
            ),
        )

    else:

        mentorship.status = (
            MentorshipStatus.REJECTED
        )


        create_notification(
            db=db,

            user_id=(
                mentorship.student_id
            ),

            notification_type=(
                "mentorship_rejected"
            ),

            title=(
                "Mentorship request update"
            ),

            message=(
                f"{get_user_display_name(mentorship.mentor)} "
                f"did not accept your mentorship "
                f"request for {mentorship.focus_area}."
            ),

            action_url=(
                "/app/mentorship"
            ),

            related_entity_type=(
                "mentorship"
            ),

            related_entity_id=(
                mentorship.id
            ),
        )


    # Mentorship decision and notification
    # are committed together.
    db.commit()

    mentorship = get_mentorship_by_id(
        db,
        mentorship.id,
    )

    return mentorship_response(
        mentorship
    )




def cancel_mentorship_request(
    db: Session,
    current_user: User,
    mentorship_id: UUID,
):

    ensure_student(
        current_user
    )

    mentorship = get_mentorship_by_id(
        db,
        mentorship_id,
    )

    if not mentorship:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Mentorship not found.",
        )

    if (
        mentorship.student_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "You cannot cancel another "
                "student's request."
            ),
        )

    if (
        mentorship.status
        != MentorshipStatus.PENDING
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only a pending mentorship "
                "request can be cancelled."
            ),
        )

    mentorship.status = (
        MentorshipStatus.CANCELLED
    )

    db.commit()

    mentorship = get_mentorship_by_id(
        db,
        mentorship.id,
    )

    return mentorship_response(
        mentorship
    )




def complete_mentorship(
    db: Session,
    current_user: User,
    mentorship_id: UUID,
):

    mentorship = get_mentorship_by_id(
        db,
        mentorship_id,
    )

    if not mentorship:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Mentorship not found.",
        )

    ensure_participant(
        current_user,
        mentorship,
    )

    if (
        mentorship.status
        != MentorshipStatus.ACTIVE
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only an active mentorship "
                "can be completed."
            ),
        )

    mentorship.status = (
        MentorshipStatus.COMPLETED
    )

    mentorship.completed_at = (
        datetime.now(
            timezone.utc
        )
    )

    for session in mentorship.sessions:

        if (
            session.status
            == MentorshipSessionStatus.SCHEDULED
        ):
            session.status = (
                MentorshipSessionStatus.CANCELLED
            )

    db.commit()

    mentorship = get_mentorship_by_id(
        db,
        mentorship.id,
    )

    return mentorship_response(
        mentorship
    )




def schedule_mentorship_session(
    db: Session,
    current_user: User,
    mentorship_id: UUID,
    request: MentorshipSessionCreateRequest,
):

    ensure_mentor(
        current_user
    )

    mentorship = get_mentorship_by_id(
        db,
        mentorship_id,
    )

    if not mentorship:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Mentorship not found.",
        )

    ensure_mentor_owns_mentorship(
        current_user,
        mentorship,
    )

    if (
        mentorship.status
        != MentorshipStatus.ACTIVE
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Sessions can only be scheduled "
                "for active mentorships."
            ),
        )

    if (
        request.scheduled_start.tzinfo
        is None
        or request.scheduled_end.tzinfo
        is None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Session date and time must "
                "include a timezone."
            ),
        )

    now = datetime.now(
        timezone.utc
    )

    if (
        request.scheduled_start
        <= now
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Session start time must "
                "be in the future."
            ),
        )

    if (
        request.scheduled_end
        <= request.scheduled_start
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Session end time must be "
                "after the start time."
            ),
        )

    create_mentorship_session(
        db=db,
        mentorship_id=mentorship.id,
        created_by_id=current_user.id,
        title=request.title.strip(),
        description=(
            request.description.strip()
            if request.description
            else None
        ),
        scheduled_start=(
            request.scheduled_start
        ),
        scheduled_end=(
            request.scheduled_end
        ),
        meeting_url=(
            request.meeting_url.strip()
            if request.meeting_url
            else None
        ),
        shared_notes=(
            request.shared_notes.strip()
            if request.shared_notes
            else None
        ),
    )

    db.commit()

    mentorship = get_mentorship_by_id(
        db,
        mentorship.id,
    )

    return mentorship_response(
        mentorship
    )




def change_session_status(
    db: Session,
    current_user: User,
    session_id: UUID,
    request: MentorshipSessionStatusRequest,
):

    ensure_mentor(
        current_user
    )

    session = (
        get_mentorship_session_by_id(
            db,
            session_id,
        )
    )

    if not session:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Mentorship session not found."
            ),
        )

    mentorship = session.mentorship

    ensure_mentor_owns_mentorship(
        current_user,
        mentorship,
    )

    if (
        session.status
        != MentorshipSessionStatus.SCHEDULED
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only scheduled sessions "
                "can be updated."
            ),
        )

    if (
        request.status
        == SessionStatusUpdate.COMPLETED
    ):

        if (
            datetime.now(
                timezone.utc
            )
            < session.scheduled_start
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail=(
                    "A session cannot be marked "
                    "completed before its start."
                ),
            )

        session.status = (
            MentorshipSessionStatus.COMPLETED
        )

    else:
        session.status = (
            MentorshipSessionStatus.CANCELLED
        )

    if (
        request.shared_notes
        is not None
    ):
        session.shared_notes = (
            request.shared_notes.strip()
            or None
        )

    db.commit()

    mentorship = get_mentorship_by_id(
        db,
        mentorship.id,
    )

    return mentorship_response(
        mentorship
    )