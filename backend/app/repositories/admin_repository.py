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

from sqlalchemy.orm import Session

from app.models.admin_audit_log import (
    AdminAuditLog,
)

from app.models.application import (
    Application,
)

from app.models.challenge import (
    Challenge,
    ChallengeStatus,
    ChallengeSubmission,
)

from app.models.mentorship import (
    Mentorship,
    MentorshipStatus,
)

from app.models.opportunity import (
    Opportunity,
    OpportunityStatus,
)

from app.models.skill import (
    Skill,
)

from app.models.user import (
    User,
    UserRole,
)


# ============================================================
# Generic Counts
# ============================================================


def count_all_users(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    User.id
                )
            )
        )
        or 0
    )


def count_users_by_role(
    db: Session,
    role: UserRole,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    User.id
                )
            ).where(
                User.role == role
            )
        )
        or 0
    )


def count_users_by_active_status(
    db: Session,
    is_active: bool,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    User.id
                )
            ).where(
                User.is_active
                == is_active
            )
        )
        or 0
    )


def count_skills(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Skill.id
                )
            )
        )
        or 0
    )


def count_opportunities(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Opportunity.id
                )
            )
        )
        or 0
    )


def count_open_opportunities(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Opportunity.id
                )
            ).where(
                Opportunity.status
                == OpportunityStatus.OPEN.value
            )
        )
        or 0
    )


def count_applications(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Application.id
                )
            )
        )
        or 0
    )


def count_mentorships(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Mentorship.id
                )
            )
        )
        or 0
    )


def count_active_mentorships(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Mentorship.id
                )
            ).where(
                Mentorship.status
                == MentorshipStatus.ACTIVE
            )
        )
        or 0
    )


def count_challenges(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Challenge.id
                )
            )
        )
        or 0
    )


def count_open_challenges(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    Challenge.id
                )
            ).where(
                Challenge.status
                == ChallengeStatus.OPEN
            )
        )
        or 0
    )


def count_challenge_submissions(
    db: Session,
) -> int:

    return (
        db.scalar(
            select(
                func.count(
                    ChallengeSubmission.id
                )
            )
        )
        or 0
    )


# ============================================================
# Users
# ============================================================


def list_users_for_admin(
    db: Session,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[
    List[User],
    int,
]:

    filters = []


    if search:

        pattern = (
            f"%{search.strip()}%"
        )

        filters.append(
            User.email.ilike(
                pattern
            )
        )


    if role is not None:

        filters.append(
            User.role == role
        )


    if is_active is not None:

        filters.append(
            User.is_active
            == is_active
        )


    count_statement = (
        select(
            func.count(
                User.id
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
        select(User)
        .where(
            *filters
        )
        .order_by(
            User.created_at.desc()
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


def get_user_for_admin(
    db: Session,
    user_id: UUID,
):

    return db.get(
        User,
        user_id,
    )


# ============================================================
# Opportunities
# ============================================================


def list_opportunities_for_admin(
    db: Session,
    search: Optional[str] = None,
    status_filter: Optional[
        OpportunityStatus
    ] = None,
    limit: int = 20,
    offset: int = 0,
):

    filters = []


    if search:

        pattern = (
            f"%{search.strip()}%"
        )

        filters.append(
            or_(
                Opportunity.title.ilike(
                    pattern
                ),

                Opportunity.company_name.ilike(
                    pattern
                ),

                User.email.ilike(
                    pattern
                ),
            )
        )


    if status_filter:

        filters.append(
            Opportunity.status
            == status_filter.value
        )


    count_statement = (
        select(
            func.count(
                Opportunity.id
            )
        )
        .select_from(
            Opportunity
        )
        .join(
            User,
            User.id
            == Opportunity.employer_id,
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
            Opportunity,
            User.email.label(
                "employer_email"
            ),
        )
        .join(
            User,
            User.id
            == Opportunity.employer_id,
        )
        .where(
            *filters
        )
        .order_by(
            Opportunity.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )


    rows = (
        db.execute(
            statement
        ).all()
    )


    return rows, total


def get_opportunity_for_admin(
    db: Session,
    opportunity_id: UUID,
):

    return db.get(
        Opportunity,
        opportunity_id,
    )


# ============================================================
# Challenges
# ============================================================


def list_challenges_for_admin(
    db: Session,
    search: Optional[str] = None,
    status_filter: Optional[
        ChallengeStatus
    ] = None,
    limit: int = 20,
    offset: int = 0,
):

    filters = []


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

                User.email.ilike(
                    pattern
                ),
            )
        )


    if status_filter:

        filters.append(
            Challenge.status
            == status_filter
        )


    count_statement = (
        select(
            func.count(
                Challenge.id
            )
        )
        .select_from(
            Challenge
        )
        .join(
            User,
            User.id
            == Challenge.employer_id,
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
            Challenge,
            User.email.label(
                "employer_email"
            ),
        )
        .join(
            User,
            User.id
            == Challenge.employer_id,
        )
        .where(
            *filters
        )
        .order_by(
            Challenge.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )


    rows = (
        db.execute(
            statement
        ).all()
    )


    return rows, total


def get_challenge_for_admin(
    db: Session,
    challenge_id: UUID,
):

    return db.get(
        Challenge,
        challenge_id,
    )


# ============================================================
# Audit Log
# ============================================================


def create_admin_audit_log(
    db: Session,
    admin_id: UUID,
    action: str,
    target_type: str,
    target_id: Optional[str],
    details=None,
):

    audit_log = AdminAuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
    )


    db.add(
        audit_log
    )


    db.flush()


    return audit_log


def list_admin_audit_logs(
    db: Session,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):

    filters = []


    if action:

        filters.append(
            AdminAuditLog.action
            == action
        )


    if target_type:

        filters.append(
            AdminAuditLog.target_type
            == target_type
        )


    count_statement = (
        select(
            func.count(
                AdminAuditLog.id
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
            AdminAuditLog,
            User.email.label(
                "admin_email"
            ),
        )
        .join(
            User,
            User.id
            == AdminAuditLog.admin_id,
        )
        .where(
            *filters
        )
        .order_by(
            AdminAuditLog.created_at.desc()
        )
        .limit(limit)
        .offset(offset)
    )


    rows = (
        db.execute(
            statement
        ).all()
    )


    return rows, total