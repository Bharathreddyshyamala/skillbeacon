from typing import Optional

from uuid import UUID

from sqlalchemy import (
    delete,
    or_,
    select,
)

from sqlalchemy.orm import (
    Session,
    selectinload,
)

from app.models.opportunity import (
    Opportunity,
    OpportunitySkill,
    OpportunityStatus,
)


# ============================================================
# Relationship loading
# ============================================================


def opportunity_load_options():

    return (
        selectinload(
            Opportunity.skills
        ).selectinload(
            OpportunitySkill.skill
        ),
    )


# ============================================================
# Get one opportunity
# ============================================================


def get_opportunity(
    db: Session,
    opportunity_id: UUID,
):

    statement = (
        select(Opportunity)
        .options(
            *opportunity_load_options()
        )
        .where(
            Opportunity.id
            == opportunity_id
        )
    )

    return db.scalar(statement)


# ============================================================
# Browse open opportunities
# ============================================================


def list_open_opportunities(
    db: Session,
    search: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    opportunity_type: Optional[str] = None,
    skill_id: Optional[UUID] = None,
):

    statement = (
        select(Opportunity)
        .options(
            *opportunity_load_options()
        )
        .where(
            Opportunity.status
            == OpportunityStatus.OPEN.value
        )
    )


    if search:

        pattern = (
            f"%{search}%"
        )

        statement = statement.where(
            or_(
                Opportunity.title.ilike(
                    pattern
                ),

                Opportunity.company_name.ilike(
                    pattern
                ),

                Opportunity.description.ilike(
                    pattern
                ),
            )
        )


    if location:

        statement = statement.where(
            Opportunity.location.ilike(
                f"%{location}%"
            )
        )


    if work_mode:

        statement = statement.where(
            Opportunity.work_mode
            == work_mode
        )


    if opportunity_type:

        statement = statement.where(
            Opportunity.opportunity_type
            == opportunity_type
        )


    if skill_id:

        statement = (
            statement
            .join(
                OpportunitySkill,
                OpportunitySkill.opportunity_id
                == Opportunity.id,
            )
            .where(
                OpportunitySkill.skill_id
                == skill_id
            )
            .distinct()
        )


    statement = statement.order_by(
        Opportunity.created_at.desc()
    )


    return list(
        db.scalars(
            statement
        ).unique()
    )


# ============================================================
# Employer's opportunities
# ============================================================


def list_my_opportunities(
    db: Session,
    employer_id: UUID,
):

    statement = (
        select(Opportunity)
        .options(
            *opportunity_load_options()
        )
        .where(
            Opportunity.employer_id
            == employer_id
        )
        .order_by(
            Opportunity.created_at.desc()
        )
    )


    return list(
        db.scalars(
            statement
        ).unique()
    )


# ============================================================
# Create
# ============================================================


def create_opportunity(
    db: Session,
    **values,
):

    opportunity = Opportunity(
        **values
    )

    db.add(
        opportunity
    )

    db.flush()

    return opportunity


# ============================================================
# Add required skill
# ============================================================


def add_opportunity_skill(
    db: Session,
    opportunity_id: UUID,
    skill_id: UUID,
    minimum_level: str,
    required: bool,
):

    opportunity_skill = (
        OpportunitySkill(
            opportunity_id=(
                opportunity_id
            ),

            skill_id=skill_id,

            minimum_level=(
                minimum_level
            ),

            required=required,
        )
    )


    db.add(
        opportunity_skill
    )


    return opportunity_skill


# ============================================================
# Clear required skills
# ============================================================


def clear_opportunity_skills(
    db: Session,
    opportunity_id: UUID,
):

    statement = (
        delete(
            OpportunitySkill
        )
        .where(
            OpportunitySkill.opportunity_id
            == opportunity_id
        )
    )


    db.execute(
        statement
    )