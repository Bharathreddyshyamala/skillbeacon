from datetime import (
    date,
    datetime,
    timezone,
)

from typing import Set
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.exc import (
    IntegrityError,
)

from sqlalchemy.orm import Session

from app.models.challenge import (
    ChallengeStatus,
    ChallengeSubmissionStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.challenge_repository import (
    add_challenge_skill,
    clear_challenge_skills,
    create_challenge,
    create_submission,
    get_challenge_by_id,
    get_existing_submission,
    get_submission_by_id,
    list_challenge_submissions,
    list_employer_challenges,
    list_open_challenges,
    list_student_submissions,
)

from app.repositories.skill_repository import (
    get_skill_by_id,
    list_user_skills,
)

from app.schemas.challenge_schema import (
    ChallengeCreateRequest,
    ChallengeStatusRequest,
    ChallengeSubmissionCreateRequest,
    ChallengeSubmissionReviewRequest,
    ChallengeUpdateRequest,
)







VALID_SUBMISSION_TRANSITIONS = {
    ChallengeSubmissionStatus.SUBMITTED: {
        ChallengeSubmissionStatus.UNDER_REVIEW,
    },

    ChallengeSubmissionStatus.UNDER_REVIEW: {
        ChallengeSubmissionStatus.ACCEPTED,
        ChallengeSubmissionStatus.REJECTED,
    },
}


TERMINAL_SUBMISSION_STATUSES: Set[
    ChallengeSubmissionStatus
] = {
    ChallengeSubmissionStatus.ACCEPTED,
    ChallengeSubmissionStatus.REJECTED,
}







def ensure_student(
    current_user: User,
):

    if (
        current_user.role
        != UserRole.STUDENT
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Only students can perform "
                "this action."
            ),
        )


def ensure_employer(
    current_user: User,
):

    if (
        current_user.role
        != UserRole.EMPLOYER
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Only employers can perform "
                "this action."
            ),
        )


def ensure_challenge_owner(
    current_user: User,
    challenge,
):

    ensure_employer(
        current_user
    )


    if (
        challenge.employer_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot manage another "
                "employer's challenge."
            ),
        )







def validate_challenge_skills(
    db: Session,
    requirements,
):

    seen = set()


    for requirement in requirements:

        if (
            requirement.skill_id
            in seen
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "A skill cannot be "
                    "added twice."
                ),
            )


        seen.add(
            requirement.skill_id
        )


        skill = get_skill_by_id(
            db,
            requirement.skill_id,
        )


        if not skill:
            raise HTTPException(
                status_code=404,
                detail=(
                    "One of the selected "
                    "skills was not found."
                ),
            )







def challenge_response(
    challenge,
):

    return {
        "id":
            challenge.id,

        "employer_id":
            challenge.employer_id,

        "title":
            challenge.title,

        "company_name":
            challenge.company_name,

        "description":
            challenge.description,

        "instructions":
            challenge.instructions,

        "deliverables":
            challenge.deliverables,

        "challenge_type":
            challenge.challenge_type,

        "difficulty":
            challenge.difficulty,

        "status":
            challenge.status,

        "deadline":
            challenge.deadline,

        "skills": [
            {
                "id":
                    requirement.id,

                "skill_id":
                    requirement.skill_id,

                "skill_name":
                    requirement.skill.name,

                "minimum_level":
                    requirement.minimum_level,

                "required":
                    requirement.required,
            }
            for requirement
            in challenge.skills
        ],

        "created_at":
            challenge.created_at,

        "updated_at":
            challenge.updated_at,
    }







def create_new_challenge(
    db: Session,
    current_user: User,
    request: ChallengeCreateRequest,
):

    ensure_employer(
        current_user
    )


    if (
        request.deadline
        and request.deadline
        < date.today()
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Challenge deadline cannot "
                "be in the past."
            ),
        )


    validate_challenge_skills(
        db,
        request.skills,
    )


    challenge = create_challenge(
        db,

        employer_id=(
            current_user.id
        ),

        title=(
            request.title.strip()
        ),

        company_name=(
            request.company_name.strip()
        ),

        description=(
            request.description.strip()
        ),

        instructions=(
            request.instructions.strip()
        ),

        deliverables=(
            request.deliverables.strip()
            if request.deliverables
            else None
        ),

        challenge_type=(
            request.challenge_type
        ),

        difficulty=(
            request.difficulty
        ),

        deadline=(
            request.deadline
        ),

        status=(
            request.status
        ),
    )


    for requirement in request.skills:

        add_challenge_skill(
            challenge=challenge,

            skill_id=(
                requirement.skill_id
            ),

            minimum_level=(
                requirement.minimum_level
            ),

            required=(
                requirement.required
            ),
        )


    db.commit()


    challenge = get_challenge_by_id(
        db,
        challenge.id,
    )


    return challenge_response(
        challenge
    )







def get_my_challenges(
    db: Session,
    current_user: User,
):

    ensure_employer(
        current_user
    )


    challenges = (
        list_employer_challenges(
            db,
            current_user.id,
        )
    )


    return [
        challenge_response(
            challenge
        )
        for challenge
        in challenges
    ]







def browse_challenges(
    db: Session,
    current_user: User,
    search=None,
    challenge_type=None,
    difficulty=None,
    skill_id=None,
    limit=20,
    offset=0,
):

    ensure_student(
        current_user
    )


    challenges, total = (
        list_open_challenges(
            db=db,
            search=search,
            challenge_type=challenge_type,
            difficulty=difficulty,
            skill_id=skill_id,
            limit=limit,
            offset=offset,
        )
    )


    return {
        "items": [
            challenge_response(
                challenge
            )
            for challenge
            in challenges
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }







def get_open_challenge(
    db: Session,
    current_user: User,
    challenge_id: UUID,
):

    ensure_student(
        current_user
    )


    challenge = get_challenge_by_id(
        db,
        challenge_id,
    )


    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )


    if (
        challenge.status
        != ChallengeStatus.OPEN
    ):
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )


    return challenge_response(
        challenge
    )







def update_existing_challenge(
    db: Session,
    current_user: User,
    challenge_id: UUID,
    request: ChallengeUpdateRequest,
):

    challenge = get_challenge_by_id(
        db,
        challenge_id,
    )


    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )


    ensure_challenge_owner(
        current_user,
        challenge,
    )


    data = request.model_dump(
        exclude_unset=True
    )


    requirements = data.pop(
        "skills",
        None,
    )


    if (
        "deadline" in data
        and data["deadline"]
        and data["deadline"]
        < date.today()
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Challenge deadline cannot "
                "be in the past."
            ),
        )


    for key, value in data.items():

        setattr(
            challenge,
            key,
            value,
        )


    if requirements is not None:

        validate_challenge_skills(
            db,
            request.skills or [],
        )


        clear_challenge_skills(
            challenge
        )


        for requirement in (
            request.skills
            or []
        ):

            add_challenge_skill(
                challenge,
                requirement.skill_id,
                requirement.minimum_level,
                requirement.required,
            )


    db.commit()


    challenge = get_challenge_by_id(
        db,
        challenge.id,
    )


    return challenge_response(
        challenge
    )







def change_challenge_status(
    db: Session,
    current_user: User,
    challenge_id: UUID,
    request: ChallengeStatusRequest,
):

    challenge = get_challenge_by_id(
        db,
        challenge_id,
    )


    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )


    ensure_challenge_owner(
        current_user,
        challenge,
    )


    if (
        request.status
        == ChallengeStatus.OPEN
        and challenge.deadline
        and challenge.deadline
        < date.today()
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "An expired challenge "
                "cannot be opened."
            ),
        )


    challenge.status = (
        request.status
    )


    db.commit()


    challenge = get_challenge_by_id(
        db,
        challenge.id,
    )


    return challenge_response(
        challenge
    )







def create_student_snapshot(
    db: Session,
    current_user: User,
):

    profile = (
        getattr(
            current_user,
            "student_profile",
            None,
        )
        or getattr(
            current_user,
            "profile",
            None,
        )
    )


    skills = list_user_skills(
        db,
        current_user.id,
    )


    skill_snapshot = []


    for user_skill in skills:

        level = (
            user_skill.level.value
            if hasattr(
                user_skill.level,
                "value",
            )
            else user_skill.level
        )


        skill_snapshot.append(
            {
                "name":
                    user_skill.skill.name,

                "level":
                    level,

                "confidence_score":
                    user_skill.confidence_score,
            }
        )


    return {
        "first_name":
            getattr(
                profile,
                "first_name",
                None,
            )
            if profile
            else None,

        "last_name":
            getattr(
                profile,
                "last_name",
                None,
            )
            if profile
            else None,

        "headline":
            getattr(
                profile,
                "headline",
                None,
            )
            if profile
            else None,

        "summary":
            getattr(
                profile,
                "summary",
                None,
            )
            if profile
            else None,

        "skills":
            skill_snapshot,
    }







def submit_challenge_solution(
    db: Session,
    current_user: User,
    challenge_id: UUID,
    request: ChallengeSubmissionCreateRequest,
):

    ensure_student(
        current_user
    )


    challenge = get_challenge_by_id(
        db,
        challenge_id,
    )


    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )


    if (
        challenge.status
        != ChallengeStatus.OPEN
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "This challenge is not open."
            ),
        )


    if (
        challenge.deadline
        and challenge.deadline
        < date.today()
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "The challenge deadline "
                "has passed."
            ),
        )


    has_content = any([
        request.submission_text
        and request.submission_text.strip(),

        request.repository_url
        and request.repository_url.strip(),

        request.demo_url
        and request.demo_url.strip(),
    ])


    if not has_content:
        raise HTTPException(
            status_code=422,
            detail=(
                "Provide submission text, "
                "a repository URL, or a demo URL."
            ),
        )


    existing = get_existing_submission(
        db,
        challenge.id,
        current_user.id,
    )


    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "You already submitted "
                "this challenge."
            ),
        )


    snapshot = create_student_snapshot(
        db,
        current_user,
    )


    submission = create_submission(
        db=db,

        challenge_id=(
            challenge.id
        ),

        student_id=(
            current_user.id
        ),

        submission_text=(
            request.submission_text.strip()
            if request.submission_text
            else None
        ),

        repository_url=(
            request.repository_url.strip()
            if request.repository_url
            else None
        ),

        demo_url=(
            request.demo_url.strip()
            if request.demo_url
            else None
        ),

        profile_snapshot=(
            snapshot
        ),
    )


    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "You already submitted "
                "this challenge."
            ),
        )


    submission = get_submission_by_id(
        db,
        submission.id,
    )


    return student_submission_response(
        submission
    )







def student_submission_response(
    submission,
):

    return {
        "id":
            submission.id,

        "challenge_id":
            submission.challenge_id,

        "challenge_title":
            submission.challenge.title,

        "company_name":
            submission.challenge.company_name,

        "status":
            submission.status,

        "submission_text":
            submission.submission_text,

        "repository_url":
            submission.repository_url,

        "demo_url":
            submission.demo_url,

        "score":
            submission.score,

        "employer_feedback":
            submission.employer_feedback,

        "created_at":
            submission.created_at,

        "updated_at":
            submission.updated_at,
    }







def employer_submission_response(
    submission,
):

    snapshot = (
        submission.profile_snapshot
        or {}
    )


    name = " ".join(
        value
        for value in [
            snapshot.get(
                "first_name"
            ),
            snapshot.get(
                "last_name"
            ),
        ]
        if value
    ).strip()


    if not name:
        name = (
            submission.student.email
        )


    return {
        "id":
            submission.id,

        "challenge_id":
            submission.challenge_id,

        "student_id":
            submission.student_id,

        "student_name":
            name,

        "student_email":
            submission.student.email,

        "status":
            submission.status,

        "submission_text":
            submission.submission_text,

        "repository_url":
            submission.repository_url,

        "demo_url":
            submission.demo_url,

        "profile_snapshot":
            snapshot,

        "score":
            submission.score,

        "employer_feedback":
            submission.employer_feedback,

        "reviewed_at":
            submission.reviewed_at,

        "created_at":
            submission.created_at,

        "updated_at":
            submission.updated_at,
    }







def get_my_challenge_submissions(
    db: Session,
    current_user: User,
    limit=20,
    offset=0,
):

    ensure_student(
        current_user
    )


    items, total = (
        list_student_submissions(
            db,
            current_user.id,
            limit,
            offset,
        )
    )


    return {
        "items": [
            student_submission_response(
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







def get_challenge_submissions(
    db: Session,
    current_user: User,
    challenge_id: UUID,
    status_filter=None,
    limit=20,
    offset=0,
):

    challenge = get_challenge_by_id(
        db,
        challenge_id,
    )


    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found.",
        )


    ensure_challenge_owner(
        current_user,
        challenge,
    )


    items, total = (
        list_challenge_submissions(
            db,
            challenge.id,
            status_filter,
            limit,
            offset,
        )
    )


    return {
        "items": [
            employer_submission_response(
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







def validate_submission_transition(
    current_status,
    new_status,
):

    if (
        current_status
        in TERMINAL_SUBMISSION_STATUSES
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "This submission is already "
                "in a terminal state."
            ),
        )


    allowed = (
        VALID_SUBMISSION_TRANSITIONS
        .get(
            current_status,
            set(),
        )
    )


    if (
        new_status
        not in allowed
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot change submission "
                f"from {current_status.value} "
                f"to {new_status.value}."
            ),
        )







def review_challenge_submission(
    db: Session,
    current_user: User,
    submission_id: UUID,
    request: ChallengeSubmissionReviewRequest,
):

    ensure_employer(
        current_user
    )


    submission = get_submission_by_id(
        db,
        submission_id,
    )


    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Submission not found.",
        )


    ensure_challenge_owner(
        current_user,
        submission.challenge,
    )


    validate_submission_transition(
        submission.status,
        request.status,
    )


    submission.status = (
        request.status
    )


    submission.score = (
        request.score
    )


    submission.employer_feedback = (
        request.employer_feedback.strip()
        if request.employer_feedback
        else None
    )


    submission.reviewed_at = (
        datetime.now(
            timezone.utc
        )
    )


    db.commit()


    submission = get_submission_by_id(
        db,
        submission.id,
    )


    return employer_submission_response(
        submission
    )