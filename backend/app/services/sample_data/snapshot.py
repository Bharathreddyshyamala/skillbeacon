from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.sample_data.helpers import (
    enum_text,
    model_for_table,
)


def build_profile_snapshot(
    db: Session,
    user,
    profile,
):

    UserSkill = model_for_table(
        "user_skills"
    )

    Skill = model_for_table(
        "skills"
    )

    rows = list(
        db.execute(
            select(
                UserSkill,
                Skill,
            )
            .join(
                Skill,
                UserSkill.skill_id
                == Skill.id,
            )
            .where(
                UserSkill.user_id
                == user.id
            )
        ).all()
    )

    skills = []

    for (
        user_skill,
        skill,
    ) in rows:

        skills.append(
            {
                "name":
                    skill.name,

                "level":
                    enum_text(
                        user_skill.level
                    ),

                "confidence_score":
                    getattr(
                        user_skill,
                        "confidence_score",
                        None,
                    ),
            }
        )

    return {
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
            skills,
    }