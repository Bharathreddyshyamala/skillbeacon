from typing import Optional

from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.models.user import (
    User,
    UserRole,
)

from app.repositories.opportunity_repository import (
    add_opportunity_skill,
    clear_opportunity_skills,
    create_opportunity,
    get_opportunity,
    list_my_opportunities,
    list_open_opportunities,
)

from app.repositories.skill_repository import (
    get_skill_by_id,
)

from app.schemas.opportunity_schema import (
    OpportunityCreateRequest,
    OpportunityStatusRequest,
    OpportunityUpdateRequest,
)


# ============================================================
# Student browse permission
# ============================================================


def ensure_opportunity_browser(
    current_user: User,
):

    allowed_roles = {
        UserRole.STUDENT,
    }


    if current_user.role not in allowed_roles:

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Only students can browse "
                "opportunities."
            ),
        )


# ============================================================
# Employer management permission
# ============================================================


def ensure_opportunity_manager(
    current_user: User,
):

    allowed_roles = {
        UserRole.EMPLOYER,
        UserRole.ADMIN,
    }


    if current_user.role not in allowed_roles:

        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Only employers or admins "
                "can manage opportunities."
            ),
        )


# ============================================================
# Ownership
# ============================================================


def ensure_opportunity_owner(
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
                "You cannot modify another "
                "employer's opportunity."
            ),
        )


# ============================================================
# Salary validation
# ============================================================


def validate_salary(
    salary_min,
    salary_max,
):

    if (
        salary_min is not None
        and salary_max is not None
        and salary_min > salary_max
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Minimum salary cannot be "
                "greater than maximum salary."
            ),
        )


# ============================================================
# Skill validation
# ============================================================


def validate_opportunity_skills(
    db: Session,
    skills,
):

    seen = set()


    for requirement in skills:

        if (
            requirement.skill_id
            in seen
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "The same skill cannot be "
                    "added more than once."
                ),
            )


        seen.add(
            requirement.skill_id
        )


        skill = get_skill_by_id(
            db,
            requirement.skill_id,
        )


        if (
            not skill
            or not skill.is_active
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "One of the selected skills "
                    "was not found."
                ),
            )


# ============================================================
# Save required skills
# ============================================================


def save_skill_requirements(
    db: Session,
    opportunity_id: UUID,
    requirements,
):

    for requirement in requirements:

        add_opportunity_skill(
            db=db,

            opportunity_id=(
                opportunity_id
            ),

            skill_id=(
                requirement.skill_id
            ),

            minimum_level=(
                requirement.minimum_level.value
            ),

            required=(
                requirement.required
            ),
        )


# ============================================================
# Student: browse
# ============================================================


def browse_opportunities(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    opportunity_type: Optional[str] = None,
    skill_id: Optional[UUID] = None,
):

    ensure_opportunity_browser(
        current_user
    )


    return list_open_opportunities(
        db=db,

        search=search,

        location=location,

        work_mode=work_mode,

        opportunity_type=(
            opportunity_type
        ),

        skill_id=skill_id,
    )


# ============================================================
# Student: detail
# ============================================================


def get_opportunity_detail(
    db: Session,
    current_user: User,
    opportunity_id: UUID,
):

    ensure_opportunity_browser(
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


    # Students should not manually access
    # draft or closed opportunities.

    if opportunity.status != "open":

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Opportunity not found."
            ),
        )


    return opportunity


# ============================================================
# Employer: get own opportunities
# ============================================================


def get_my_opportunities(
    db: Session,
    current_user: User,
):

    ensure_opportunity_manager(
        current_user
    )


    return list_my_opportunities(
        db,
        current_user.id,
    )


# ============================================================
# Employer: create
# ============================================================


def create_new_opportunity(
    db: Session,
    current_user: User,
    request: OpportunityCreateRequest,
):

    ensure_opportunity_manager(
        current_user
    )


    validate_salary(
        request.salary_min,
        request.salary_max,
    )


    validate_opportunity_skills(
        db,
        request.skills,
    )


    opportunity = create_opportunity(
        db,

        employer_id=(
            current_user.id
        ),

        company_name=(
            request.company_name
        ),

        title=request.title,

        description=(
            request.description
        ),

        location=(
            request.location
        ),

        work_mode=(
            request.work_mode.value
        ),

        opportunity_type=(
            request.opportunity_type.value
        ),

        employment_type=(
            request.employment_type.value
            if request.employment_type
            else None
        ),

        salary_min=(
            request.salary_min
        ),

        salary_max=(
            request.salary_max
        ),

        currency=(
            request.currency.upper()
        ),

        application_url=(
            request.application_url
        ),

        deadline=(
            request.deadline
        ),

        status=(
            request.status.value
        ),
    )


    save_skill_requirements(
        db,
        opportunity.id,
        request.skills,
    )


    db.commit()


    return get_opportunity(
        db,
        opportunity.id,
    )


# ============================================================
# Employer: update
# ============================================================


def update_existing_opportunity(
    db: Session,
    current_user: User,
    opportunity_id: UUID,
    request: OpportunityUpdateRequest,
):

    ensure_opportunity_manager(
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


    ensure_opportunity_owner(
        current_user,
        opportunity,
    )


    data = request.model_dump(
        exclude_unset=True
    )


    requirements = data.pop(
        "skills",
        None,
    )


    prospective_min = data.get(
        "salary_min",
        opportunity.salary_min,
    )


    prospective_max = data.get(
        "salary_max",
        opportunity.salary_max,
    )


    validate_salary(
        prospective_min,
        prospective_max,
    )


    enum_fields = {
        "work_mode",
        "opportunity_type",
        "employment_type",
    }


    for field_name, value in data.items():

        if (
            field_name in enum_fields
            and value is not None
            and hasattr(
                value,
                "value"
            )
        ):

            value = value.value


        if (
            field_name == "currency"
            and value
        ):

            value = value.upper()


        setattr(
            opportunity,
            field_name,
            value,
        )


    if requirements is not None:

        requested_skills = (
            request.skills or []
        )


        validate_opportunity_skills(
            db,
            requested_skills,
        )


        clear_opportunity_skills(
            db,
            opportunity.id,
        )


        save_skill_requirements(
            db,
            opportunity.id,
            requested_skills,
        )


    db.commit()


    return get_opportunity(
        db,
        opportunity.id,
    )


# ============================================================
# Employer: status
# ============================================================


def change_opportunity_status(
    db: Session,
    current_user: User,
    opportunity_id: UUID,
    request: OpportunityStatusRequest,
):

    ensure_opportunity_manager(
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


    ensure_opportunity_owner(
        current_user,
        opportunity,
    )


    opportunity.status = (
        request.status.value
    )


    db.commit()


    return get_opportunity(
        db,
        opportunity.id,
    )