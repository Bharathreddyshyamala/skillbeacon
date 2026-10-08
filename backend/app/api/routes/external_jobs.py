from typing import Literal, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.database import get_db

from app.models.user import (
    User,
    UserRole,
)
from app.models.external_job import (
    ExternalJob,
)
from app.schemas.external_job import (
    ExternalJobListResponse,
    ExternalJobResponse,
)


router = APIRouter(
    prefix="/external-jobs",
    tags=["External Jobs"],
)


def require_student(
    current_user: User = Depends(
        get_current_user
    ),
):

    if (
        current_user.role
        != UserRole.STUDENT
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Student access required"
            ),
        )

    return current_user


@router.get(
    "",
    response_model=(
        ExternalJobListResponse
    ),
)
def list_external_jobs(
    search: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    sort: Literal[
        "posted",
        "source",
    ] = "posted",
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    _: User = Depends(
        require_student
    ),
):

    query = (
        db.query(ExternalJob)
        .filter(
            ExternalJob.is_active
            .is_(True)
        )
    )

    if search:
        pattern = f"%{search}%"

        query = query.filter(
            or_(
                ExternalJob.title
                .ilike(pattern),
                ExternalJob.description
                .ilike(pattern),
                ExternalJob.company_name
                .ilike(pattern),
            )
        )

    if company:
        query = query.filter(
            ExternalJob.company_name
            .ilike(
                f"%{company}%"
            )
        )

    if location:
        query = query.filter(
            ExternalJob.location
            .ilike(
                f"%{location}%"
            )
        )

    total = query.count()

    if sort == "source":
        query = query.order_by(
            ExternalJob.source_rank
            .asc()
            .nullslast(),
            ExternalJob.posted_at
            .desc()
            .nullslast(),
            ExternalJob.id.asc(),
        )
    else:
        query = query.order_by(
            ExternalJob.posted_at
            .desc()
            .nullslast(),
            ExternalJob.created_at
            .desc(),
        )

    jobs = (
        query
        .offset(
            (page - 1)
            * page_size
        )
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": jobs,
    }


@router.get(
    "/{job_id}",
    response_model=(
        ExternalJobResponse
    ),
)
def get_external_job(
    job_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_student
    ),
):

    job = (
        db.query(ExternalJob)
        .filter(
            ExternalJob.id
            == job_id,
            ExternalJob.is_active
            .is_(True),
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job
