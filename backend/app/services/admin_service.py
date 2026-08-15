from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models.challenge import (
    ChallengeStatus,
)

from app.models.opportunity import (
    OpportunityStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.admin_repository import (
    count_active_mentorships,
    count_all_users,
    count_applications,
    count_challenge_submissions,
    count_challenges,
    count_mentorships,
    count_open_challenges,
    count_open_opportunities,
    count_opportunities,
    count_skills,
    count_users_by_active_status,
    count_users_by_role,
    create_admin_audit_log,
    get_challenge_for_admin,
    get_opportunity_for_admin,
    get_user_for_admin,
    list_admin_audit_logs,
    list_challenges_for_admin,
    list_opportunities_for_admin,
    list_users_for_admin,
)

from app.schemas.admin_schema import (
    AdminChallengeStatusRequest,
    AdminOpportunityStatusRequest,
    AdminUserStatusRequest,
    AdminUserVerificationRequest,
)

from app.services.notification_service import (
    create_notification,
)


# ============================================================
# Helpers
# ============================================================


def enum_value(
    value,
):

    if hasattr(
        value,
        "value",
    ):
        return value.value

    return value


# ============================================================
# Security
# ============================================================


def ensure_admin(
    current_user: User,
):

    if (
        current_user.role
        != UserRole.ADMIN
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Administrator access "
                "is required."
            ),
        )


# ============================================================
# Response Builders
# ============================================================


def admin_user_response(
    user,
):

    return {
        "id":
            user.id,

        "email":
            user.email,

        "role":
            enum_value(
                user.role
            ),

        "is_active":
            user.is_active,

        "is_verified":
            user.is_verified,

        "created_at":
            user.created_at,

        "updated_at":
            user.updated_at,
    }


def admin_opportunity_response(
    opportunity,
    employer_email,
):

    return {
        "id":
            opportunity.id,

        "employer_id":
            opportunity.employer_id,

        "employer_email":
            employer_email,

        "title":
            opportunity.title,

        "company_name":
            opportunity.company_name,

        "status":
            enum_value(
                opportunity.status
            ),

        "deadline":
            opportunity.deadline,

        "created_at":
            opportunity.created_at,

        "updated_at":
            opportunity.updated_at,
    }


def admin_challenge_response(
    challenge,
    employer_email,
):

    return {
        "id":
            challenge.id,

        "employer_id":
            challenge.employer_id,

        "employer_email":
            employer_email,

        "title":
            challenge.title,

        "company_name":
            challenge.company_name,

        "challenge_type":
            enum_value(
                challenge.challenge_type
            ),

        "difficulty":
            enum_value(
                challenge.difficulty
            ),

        "status":
            enum_value(
                challenge.status
            ),

        "deadline":
            challenge.deadline,

        "created_at":
            challenge.created_at,

        "updated_at":
            challenge.updated_at,
    }


# ============================================================
# Dashboard
# ============================================================


def get_admin_dashboard(
    db: Session,
    current_user: User,
):

    ensure_admin(
        current_user
    )


    return {
        "total_users":
            count_all_users(
                db
            ),

        "students":
            count_users_by_role(
                db,
                UserRole.STUDENT,
            ),

        "mentors":
            count_users_by_role(
                db,
                UserRole.MENTOR,
            ),

        "employers":
            count_users_by_role(
                db,
                UserRole.EMPLOYER,
            ),

        "admins":
            count_users_by_role(
                db,
                UserRole.ADMIN,
            ),

        "active_users":
            count_users_by_active_status(
                db,
                True,
            ),

        "inactive_users":
            count_users_by_active_status(
                db,
                False,
            ),

        "total_skills":
            count_skills(
                db
            ),

        "total_opportunities":
            count_opportunities(
                db
            ),

        "open_opportunities":
            count_open_opportunities(
                db
            ),

        "total_applications":
            count_applications(
                db
            ),

        "total_mentorships":
            count_mentorships(
                db
            ),

        "active_mentorships":
            count_active_mentorships(
                db
            ),

        "total_challenges":
            count_challenges(
                db
            ),

        "open_challenges":
            count_open_challenges(
                db
            ),

        "challenge_submissions":
            count_challenge_submissions(
                db
            ),
    }


# ============================================================
# Users
# ============================================================


def get_admin_users(
    db: Session,
    current_user: User,
    search=None,
    role=None,
    is_active=None,
    limit=20,
    offset=0,
):

    ensure_admin(
        current_user
    )


    items, total = (
        list_users_for_admin(
            db=db,
            search=search,
            role=role,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
    )


    return {
        "items": [
            admin_user_response(
                user
            )
            for user in items
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }


def get_admin_user(
    db: Session,
    current_user: User,
    user_id: UUID,
):

    ensure_admin(
        current_user
    )


    user = get_user_for_admin(
        db,
        user_id,
    )


    if not user:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="User not found.",
        )


    return admin_user_response(
        user
    )


# ============================================================
# Activate / Deactivate User
# ============================================================


def change_user_active_status(
    db: Session,
    current_user: User,
    user_id: UUID,
    request: AdminUserStatusRequest,
):

    ensure_admin(
        current_user
    )


    user = get_user_for_admin(
        db,
        user_id,
    )


    if not user:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="User not found.",
        )


    # -----------------------------------------------
    # Prevent accidental self-lockout
    # -----------------------------------------------

    if (
        user.id
        == current_user.id
        and request.is_active
        is False
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "You cannot deactivate "
                "your own administrator account."
            ),
        )


    # -----------------------------------------------
    # Admin accounts should not be managed
    # through normal user moderation
    # -----------------------------------------------

    if (
        user.role
        == UserRole.ADMIN
        and user.id
        != current_user.id
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Administrator accounts cannot "
                "be modified from user moderation."
            ),
        )


    old_status = (
        user.is_active
    )


    user.is_active = (
        request.is_active
    )


    if request.is_active:

        action = (
            "activate_user"
        )

        notification_title = (
            "Account reactivated"
        )

        notification_message = (
            "Your SkillBeacon account "
            "has been reactivated."
        )

    else:

        action = (
            "deactivate_user"
        )

        notification_title = (
            "Account status updated"
        )

        notification_message = (
            "Your SkillBeacon account "
            "has been deactivated "
            "by platform moderation."
        )


    create_admin_audit_log(
        db=db,

        admin_id=(
            current_user.id
        ),

        action=action,

        target_type="user",

        target_id=str(
            user.id
        ),

        details={
            "email":
                user.email,

            "old_is_active":
                old_status,

            "new_is_active":
                request.is_active,
        },
    )


    create_notification(
        db=db,

        user_id=(
            user.id
        ),

        notification_type=(
            "account_status"
        ),

        title=(
            notification_title
        ),

        message=(
            notification_message
        ),

        action_url=(
            "/app/dashboard"
        ),

        related_entity_type=(
            "user"
        ),

        related_entity_id=(
            user.id
        ),
    )


    db.commit()


    return admin_user_response(
        user
    )


# ============================================================
# Verify / Unverify User
# ============================================================


def change_user_verification(
    db: Session,
    current_user: User,
    user_id: UUID,
    request: AdminUserVerificationRequest,
):

    ensure_admin(
        current_user
    )


    user = get_user_for_admin(
        db,
        user_id,
    )


    if not user:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="User not found.",
        )


    if (
        user.role
        == UserRole.ADMIN
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Administrator verification "
                "cannot be changed here."
            ),
        )


    old_status = (
        user.is_verified
    )


    user.is_verified = (
        request.is_verified
    )


    if request.is_verified:

        action = (
            "verify_user"
        )

        title = (
            "Account verified"
        )

        message = (
            "Your SkillBeacon account "
            "has been verified."
        )

    else:

        action = (
            "unverify_user"
        )

        title = (
            "Verification removed"
        )

        message = (
            "Your SkillBeacon account "
            "verification has been removed."
        )


    create_admin_audit_log(
        db=db,

        admin_id=(
            current_user.id
        ),

        action=action,

        target_type="user",

        target_id=str(
            user.id
        ),

        details={
            "email":
                user.email,

            "old_is_verified":
                old_status,

            "new_is_verified":
                request.is_verified,
        },
    )


    create_notification(
        db=db,

        user_id=(
            user.id
        ),

        notification_type=(
            "verification_status"
        ),

        title=title,

        message=message,

        action_url=(
            "/app/profile"
        ),

        related_entity_type=(
            "user"
        ),

        related_entity_id=(
            user.id
        ),
    )


    db.commit()


    return admin_user_response(
        user
    )


# ============================================================
# Opportunity List
# ============================================================


def get_admin_opportunities(
    db: Session,
    current_user: User,
    search=None,
    status_filter=None,
    limit=20,
    offset=0,
):

    ensure_admin(
        current_user
    )


    rows, total = (
        list_opportunities_for_admin(
            db=db,
            search=search,
            status_filter=(
                status_filter
            ),
            limit=limit,
            offset=offset,
        )
    )


    return {
        "items": [
            admin_opportunity_response(
                row[0],
                row[1],
            )
            for row in rows
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }


# ============================================================
# Opportunity Moderation
# ============================================================


def moderate_opportunity_status(
    db: Session,
    current_user: User,
    opportunity_id: UUID,
    request: AdminOpportunityStatusRequest,
):

    ensure_admin(
        current_user
    )


    opportunity = (
        get_opportunity_for_admin(
            db,
            opportunity_id,
        )
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


    allowed_statuses = {
        OpportunityStatus.OPEN,
        OpportunityStatus.CLOSED,
    }


    if (
        request.status
        not in allowed_statuses
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Admin moderation can only "
                "open or close an opportunity."
            ),
        )


    old_status = enum_value(
        opportunity.status
    )


    opportunity.status = (
        request.status.value
    )


    if (
        request.status
        == OpportunityStatus.CLOSED
    ):

        action = (
            "close_opportunity"
        )

        title = (
            "Opportunity closed"
        )

        message = (
            f'Your opportunity '
            f'"{opportunity.title}" '
            f'was closed by '
            f'platform moderation.'
        )

    else:

        action = (
            "reopen_opportunity"
        )

        title = (
            "Opportunity reopened"
        )

        message = (
            f'Your opportunity '
            f'"{opportunity.title}" '
            f'was reopened by '
            f'platform moderation.'
        )


    create_admin_audit_log(
        db=db,

        admin_id=(
            current_user.id
        ),

        action=action,

        target_type=(
            "opportunity"
        ),

        target_id=str(
            opportunity.id
        ),

        details={
            "title":
                opportunity.title,

            "company_name":
                opportunity.company_name,

            "old_status":
                old_status,

            "new_status":
                request.status.value,
        },
    )


    create_notification(
        db=db,

        user_id=(
            opportunity.employer_id
        ),

        notification_type=(
            "opportunity_moderation"
        ),

        title=title,

        message=message,

        action_url=(
            "/app/opportunities/manage"
        ),

        related_entity_type=(
            "opportunity"
        ),

        related_entity_id=(
            opportunity.id
        ),
    )


    db.commit()


    return {
        "message":
            (
                "Opportunity status "
                "updated successfully."
            ),

        "id":
            opportunity.id,

        "status":
            request.status.value,
    }


# ============================================================
# Challenge List
# ============================================================


def get_admin_challenges(
    db: Session,
    current_user: User,
    search=None,
    status_filter=None,
    limit=20,
    offset=0,
):

    ensure_admin(
        current_user
    )


    rows, total = (
        list_challenges_for_admin(
            db=db,
            search=search,
            status_filter=(
                status_filter
            ),
            limit=limit,
            offset=offset,
        )
    )


    return {
        "items": [
            admin_challenge_response(
                row[0],
                row[1],
            )
            for row in rows
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }


# ============================================================
# Challenge Moderation
# ============================================================


def moderate_challenge_status(
    db: Session,
    current_user: User,
    challenge_id: UUID,
    request: AdminChallengeStatusRequest,
):

    ensure_admin(
        current_user
    )


    challenge = (
        get_challenge_for_admin(
            db,
            challenge_id,
        )
    )


    if not challenge:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Challenge not found."
            ),
        )


    allowed_statuses = {
        ChallengeStatus.OPEN,
        ChallengeStatus.CLOSED,
    }


    if (
        request.status
        not in allowed_statuses
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Admin moderation can only "
                "open or close a challenge."
            ),
        )


    old_status = enum_value(
        challenge.status
    )


    challenge.status = (
        request.status
    )


    if (
        request.status
        == ChallengeStatus.CLOSED
    ):

        action = (
            "close_challenge"
        )

        title = (
            "Challenge closed"
        )

        message = (
            f'Your challenge '
            f'"{challenge.title}" '
            f'was closed by '
            f'platform moderation.'
        )

    else:

        action = (
            "reopen_challenge"
        )

        title = (
            "Challenge reopened"
        )

        message = (
            f'Your challenge '
            f'"{challenge.title}" '
            f'was reopened by '
            f'platform moderation.'
        )


    create_admin_audit_log(
        db=db,

        admin_id=(
            current_user.id
        ),

        action=action,

        target_type=(
            "challenge"
        ),

        target_id=str(
            challenge.id
        ),

        details={
            "title":
                challenge.title,

            "company_name":
                challenge.company_name,

            "old_status":
                old_status,

            "new_status":
                request.status.value,
        },
    )


    create_notification(
        db=db,

        user_id=(
            challenge.employer_id
        ),

        notification_type=(
            "challenge_moderation"
        ),

        title=title,

        message=message,

        action_url=(
            "/app/challenges/manage"
        ),

        related_entity_type=(
            "challenge"
        ),

        related_entity_id=(
            challenge.id
        ),
    )


    db.commit()


    return {
        "message":
            (
                "Challenge status "
                "updated successfully."
            ),

        "id":
            challenge.id,

        "status":
            request.status.value,
    }


# ============================================================
# Audit Logs
# ============================================================


def get_admin_audit_logs(
    db: Session,
    current_user: User,
    action=None,
    target_type=None,
    limit=50,
    offset=0,
):

    ensure_admin(
        current_user
    )


    rows, total = (
        list_admin_audit_logs(
            db=db,
            action=action,
            target_type=target_type,
            limit=limit,
            offset=offset,
        )
    )


    return {
        "items": [
            {
                "id":
                    row[0].id,

                "admin_id":
                    row[0].admin_id,

                "admin_email":
                    row[1],

                "action":
                    row[0].action,

                "target_type":
                    row[0].target_type,

                "target_id":
                    row[0].target_id,

                "details":
                    row[0].details,

                "created_at":
                    row[0].created_at,
            }

            for row in rows
        ],

        "total":
            total,

        "limit":
            limit,

        "offset":
            offset,
    }