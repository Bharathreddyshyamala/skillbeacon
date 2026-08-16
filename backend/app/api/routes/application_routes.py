import mimetypes

from typing import Optional

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from fastapi.responses import (
    FileResponse,
    RedirectResponse,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user

from app.models.application import (
    ApplicationStatus,
)

from app.models.user import User

from app.schemas.application_schema import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationStatusRequest,
    EmployerApplicationListResponse,
    EmployerApplicationResponse,
    StudentApplicationListResponse,
    StudentApplicationResponse,
)

from app.services.application_service import (
    change_application_note,
    change_application_status,
    get_application_resume,
    get_my_application,
    get_my_applications,
    get_opportunity_applications,
    submit_application,
    withdraw_my_application,
)


router = APIRouter(
    tags=["Applications"],
)




@router.post(
    "/applications",
    response_model=(
        StudentApplicationResponse
    ),
    status_code=201,
)
def create_application_route(
    request: ApplicationCreateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return submit_application(
        db,
        current_user,
        request,
    )




@router.get(
    "/applications/me",
    response_model=(
        StudentApplicationListResponse
    ),
)
def my_applications_route(
    status_filter: Optional[
        ApplicationStatus
    ] = Query(
        default=None,
        alias="status",
    ),

    opportunity_id: Optional[
        UUID
    ] = Query(
        default=None
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_my_applications(
        db=db,

        current_user=(
            current_user
        ),

        status_filter=(
            status_filter
        ),

        opportunity_id=(
            opportunity_id
        ),

        limit=limit,

        offset=offset,
    )




@router.get(
    "/opportunities/{opportunity_id}/applications",
    response_model=(
        EmployerApplicationListResponse
    ),
)
def opportunity_applications_route(
    opportunity_id: UUID,

    status_filter: Optional[
        ApplicationStatus
    ] = Query(
        default=None,
        alias="status",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_opportunity_applications(
        db=db,

        current_user=current_user,

        opportunity_id=(
            opportunity_id
        ),

        status_filter=(
            status_filter
        ),

        limit=limit,

        offset=offset,
    )




@router.get(
    "/applications/{application_id}",
    response_model=(
        StudentApplicationResponse
    ),
)
def application_detail_route(
    application_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_my_application(
        db,
        current_user,
        application_id,
    )




@router.patch(
    "/applications/{application_id}/withdraw",
    response_model=(
        StudentApplicationResponse
    ),
)
def withdraw_application_route(
    application_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return withdraw_my_application(
        db,
        current_user,
        application_id,
    )




@router.patch(
    "/applications/{application_id}/status",
    response_model=(
        EmployerApplicationResponse
    ),
)
def application_status_route(
    application_id: UUID,

    request: ApplicationStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_application_status(
        db,
        current_user,
        application_id,
        request,
    )




@router.patch(
    "/applications/{application_id}/note",
    response_model=(
        EmployerApplicationResponse
    ),
)
def application_note_route(
    application_id: UUID,

    request: ApplicationNoteRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_application_note(
        db,
        current_user,
        application_id,
        request,
    )




@router.get(
    "/applications/{application_id}/resume"
)
def application_resume_route(
    application_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    resume_target = get_application_resume(
        db,
        current_user,
        application_id,
    )


    if isinstance(resume_target, str) and (
        resume_target.startswith("http://")
        or resume_target.startswith("https://")
    ):
        return RedirectResponse(
            url=resume_target,
            status_code=307,
        )


    media_type, _ = (
        mimetypes.guess_type(
            str(resume_target)
        )
    )


    return FileResponse(
        path=str(resume_target),

        filename=(
            resume_target.name
            if hasattr(resume_target, "name")
            else "resume"
        ),

        media_type=(
            media_type
            or "application/octet-stream"
        ),
    )