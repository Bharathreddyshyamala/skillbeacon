from typing import (
    List,
    Optional,
    Tuple,
)

from uuid import UUID

from sqlalchemy import (
    func,
    or_,
    select,
)

from sqlalchemy.orm import (
    Session,
    joinedload,
    selectinload,
)

from app.models.mentorship import (
    Mentorship,
    MentorshipSession,
    MentorshipSessionStatus,
    MentorshipStatus,
)

from app.models.skill import (
    UserSkill,
)

from app.models.user import (
    User,
    UserRole,
)




def mentorship_load_options():
    return (
        joinedload(
            Mentorship.student
        ),
        joinedload(
            Mentorship.mentor
        ),
        selectinload(
            Mentorship.sessions
        ),
    )




def get_user_by_id(
    db: Session,
    user_id: UUID,
):
    return db.get(
        User,
        user_id,
    )




def list_mentors(
    db: Session,
    search: Optional[str] = None,
    skill_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[List[User], int]:

    filters = [
        User.role == UserRole.MENTOR,
        User.is_active.is_(True),
    ]

    statement = (
        select(User)
        .where(
            *filters
        )
    )

    count_statement = (
        select(
            func.count(
                func.distinct(
                    User.id
                )
            )
        )
        .select_from(User)
        .where(
            *filters
        )
    )

    if search:
        search_pattern = (
            f"%{search.strip()}%"
        )

        search_condition = or_(
            User.email.ilike(
                search_pattern
            ),
        )

        statement = statement.where(
            search_condition
        )

        count_statement = (
            count_statement.where(
                search_condition
            )
        )

    if skill_id:
        statement = (
            statement
            .join(
                UserSkill,
                UserSkill.user_id
                == User.id,
            )
            .where(
                UserSkill.skill_id
                == skill_id
            )
        )

        count_statement = (
            count_statement
            .join(
                UserSkill,
                UserSkill.user_id
                == User.id,
            )
            .where(
                UserSkill.skill_id
                == skill_id
            )
        )

    total = (
        db.scalar(
            count_statement
        )
        or 0
    )

    statement = (
        statement
        .distinct()
        .order_by(
            User.email.asc()
        )
        .limit(limit)
        .offset(offset)
    )

    mentors = list(
        db.scalars(
            statement
        ).unique()
    )

    return mentors, total


def list_mentor_skills(
    db: Session,
    mentor_id: UUID,
):

    statement = (
        select(UserSkill)
        .options(
            joinedload(
                UserSkill.skill
            )
        )
        .where(
            UserSkill.user_id
            == mentor_id
        )
        .order_by(
            UserSkill.confidence_score.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).unique()
    )




def get_active_mentorship_for_pair(
    db: Session,
    student_id: UUID,
    mentor_id: UUID,
):

    statement = (
        select(Mentorship)
        .where(
            Mentorship.student_id
            == student_id,

            Mentorship.mentor_id
            == mentor_id,

            Mentorship.status.in_(
                [
                    MentorshipStatus.PENDING,
                    MentorshipStatus.ACTIVE,
                ]
            ),
        )
    )

    return db.scalar(
        statement
    )




def create_mentorship(
    db: Session,
    student_id: UUID,
    mentor_id: UUID,
    focus_area: str,
    goals: str,
    message: Optional[str],
):

    mentorship = Mentorship(
        student_id=student_id,
        mentor_id=mentor_id,
        focus_area=focus_area,
        goals=goals,
        message=message,
        status=MentorshipStatus.PENDING,
    )

    db.add(
        mentorship
    )

    db.flush()

    return mentorship




def get_mentorship_by_id(
    db: Session,
    mentorship_id: UUID,
):

    statement = (
        select(Mentorship)
        .options(
            *mentorship_load_options()
        )
        .where(
            Mentorship.id
            == mentorship_id
        )
    )

    return db.scalar(
        statement
    )




def list_user_mentorships(
    db: Session,
    user_id: UUID,
    as_mentor: bool,
    status_filter: Optional[
        MentorshipStatus
    ] = None,
    limit: int = 20,
    offset: int = 0,
):

    if as_mentor:
        owner_condition = (
            Mentorship.mentor_id
            == user_id
        )
    else:
        owner_condition = (
            Mentorship.student_id
            == user_id
        )

    filters = [
        owner_condition
    ]

    if status_filter:
        filters.append(
            Mentorship.status
            == status_filter
        )

    count_statement = (
        select(
            func.count(
                Mentorship.id
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
        select(Mentorship)
        .options(
            *mentorship_load_options()
        )
        .where(
            *filters
        )
        .order_by(
            Mentorship.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )

    items = list(
        db.scalars(
            statement
        ).unique()
    )

    return items, total




def create_mentorship_session(
    db: Session,
    mentorship_id: UUID,
    created_by_id: UUID,
    title: str,
    description: Optional[str],
    scheduled_start,
    scheduled_end,
    meeting_url: Optional[str],
    shared_notes: Optional[str],
):

    session = MentorshipSession(
        mentorship_id=mentorship_id,
        created_by_id=created_by_id,
        title=title,
        description=description,
        scheduled_start=scheduled_start,
        scheduled_end=scheduled_end,
        meeting_url=meeting_url,
        shared_notes=shared_notes,
        status=(
            MentorshipSessionStatus.SCHEDULED
        ),
    )

    db.add(
        session
    )

    db.flush()

    return session




def get_mentorship_session_by_id(
    db: Session,
    session_id: UUID,
):

    statement = (
        select(MentorshipSession)
        .options(
            joinedload(
                MentorshipSession.mentorship
            ).joinedload(
                Mentorship.student
            ),

            joinedload(
                MentorshipSession.mentorship
            ).joinedload(
                Mentorship.mentor
            ),
        )
        .where(
            MentorshipSession.id
            == session_id
        )
    )

    return db.scalar(
        statement
    )