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

from app.models.challenge import (
    Challenge,
    ChallengeSkill,
    ChallengeStatus,
    ChallengeSubmission,
    ChallengeSubmissionStatus,
)







def challenge_load_options():
    return (
        selectinload(
            Challenge.skills
        ).joinedload(
            ChallengeSkill.skill
        ),
    )


def submission_load_options():
    return (
        joinedload(
            ChallengeSubmission.challenge
        ),

        joinedload(
            ChallengeSubmission.student
        ),
    )







def create_challenge(
    db: Session,
    **values,
):
    challenge = Challenge(
        **values
    )

    db.add(
        challenge
    )

    db.flush()

    return challenge


def get_challenge_by_id(
    db: Session,
    challenge_id: UUID,
):
    statement = (
        select(Challenge)
        .options(
            *challenge_load_options()
        )
        .where(
            Challenge.id
            == challenge_id
        )
    )

    return db.scalar(
        statement
    )


def clear_challenge_skills(
    challenge: Challenge,
):
    challenge.skills.clear()


def add_challenge_skill(
    challenge: Challenge,
    skill_id: UUID,
    minimum_level,
    required: bool,
):
    requirement = ChallengeSkill(
        skill_id=skill_id,
        minimum_level=minimum_level,
        required=required,
    )

    challenge.skills.append(
        requirement
    )

    return requirement







def list_open_challenges(
    db: Session,
    search: Optional[str] = None,
    challenge_type=None,
    difficulty=None,
    skill_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0,
):

    filters = [
        Challenge.status
        == ChallengeStatus.OPEN
    ]


    if search:
        pattern = (
            f"%{search.strip()}%"
        )

        filters.append(
            or_(
                Challenge.title.ilike(
                    pattern
                ),
                Challenge.company_name.ilike(
                    pattern
                ),
                Challenge.description.ilike(
                    pattern
                ),
            )
        )


    if challenge_type:
        filters.append(
            Challenge.challenge_type
            == challenge_type
        )


    if difficulty:
        filters.append(
            Challenge.difficulty
            == difficulty
        )


    statement = (
        select(Challenge)
        .options(
            *challenge_load_options()
        )
        .where(
            *filters
        )
    )


    count_statement = (
        select(
            func.count(
                func.distinct(
                    Challenge.id
                )
            )
        )
        .select_from(
            Challenge
        )
        .where(
            *filters
        )
    )


    if skill_id:
        statement = (
            statement
            .join(
                ChallengeSkill
            )
            .where(
                ChallengeSkill.skill_id
                == skill_id
            )
        )

        count_statement = (
            count_statement
            .join(
                ChallengeSkill
            )
            .where(
                ChallengeSkill.skill_id
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
            Challenge.created_at.desc()
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







def list_employer_challenges(
    db: Session,
    employer_id: UUID,
):

    statement = (
        select(Challenge)
        .options(
            *challenge_load_options()
        )
        .where(
            Challenge.employer_id
            == employer_id
        )
        .order_by(
            Challenge.created_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).unique()
    )







def create_submission(
    db: Session,
    challenge_id: UUID,
    student_id: UUID,
    submission_text,
    repository_url,
    demo_url,
    profile_snapshot,
):

    submission = ChallengeSubmission(
        challenge_id=challenge_id,
        student_id=student_id,
        submission_text=submission_text,
        repository_url=repository_url,
        demo_url=demo_url,
        profile_snapshot=profile_snapshot,
        status=(
            ChallengeSubmissionStatus.SUBMITTED
        ),
    )

    db.add(
        submission
    )

    db.flush()

    return submission


def get_existing_submission(
    db: Session,
    challenge_id: UUID,
    student_id: UUID,
):

    statement = (
        select(
            ChallengeSubmission
        )
        .where(
            ChallengeSubmission.challenge_id
            == challenge_id,

            ChallengeSubmission.student_id
            == student_id,
        )
    )

    return db.scalar(
        statement
    )


def get_submission_by_id(
    db: Session,
    submission_id: UUID,
):

    statement = (
        select(
            ChallengeSubmission
        )
        .options(
            *submission_load_options()
        )
        .where(
            ChallengeSubmission.id
            == submission_id
        )
    )

    return db.scalar(
        statement
    )







def list_student_submissions(
    db: Session,
    student_id: UUID,
    limit: int = 20,
    offset: int = 0,
):

    count_statement = (
        select(
            func.count(
                ChallengeSubmission.id
            )
        )
        .where(
            ChallengeSubmission.student_id
            == student_id
        )
    )


    total = (
        db.scalar(
            count_statement
        )
        or 0
    )


    statement = (
        select(
            ChallengeSubmission
        )
        .options(
            *submission_load_options()
        )
        .where(
            ChallengeSubmission.student_id
            == student_id
        )
        .order_by(
            ChallengeSubmission
            .created_at
            .desc()
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







def list_challenge_submissions(
    db: Session,
    challenge_id: UUID,
    status_filter=None,
    limit: int = 20,
    offset: int = 0,
):

    filters = [
        ChallengeSubmission.challenge_id
        == challenge_id
    ]


    if status_filter:
        filters.append(
            ChallengeSubmission.status
            == status_filter
        )


    count_statement = (
        select(
            func.count(
                ChallengeSubmission.id
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
        select(
            ChallengeSubmission
        )
        .options(
            *submission_load_options()
        )
        .where(
            *filters
        )
        .order_by(
            ChallengeSubmission
            .created_at
            .desc()
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