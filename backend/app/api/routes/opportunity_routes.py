from typing import (
    List,
    Optional,
)

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from sqlalchemy.orm import Session


from app.core.database import get_db
from app.api.dependencies import get_current_user

from app.models.user import User

from app.schemas.opportunity_schema import (
    OpportunityCreateRequest,
    OpportunityResponse,
    OpportunityStatusRequest,
    OpportunityUpdateRequest,
)

from app.services.opportunity_service import (
    browse_opportunities,
    change_opportunity_status,
    create_new_opportunity,
    get_my_opportunities,
    get_opportunity_detail,
    update_existing_opportunity,
)


router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"],
)




@router.get(
    "",
    response_model=List[
        OpportunityResponse
    ],
)
def list_opportunities(
    search: Optional[str] = Query(
        default=None
    ),

    location: Optional[str] = Query(
        default=None
    ),

    work_mode: Optional[str] = Query(
        default=None
    ),

    opportunity_type: Optional[
        str
    ] = Query(
        default=None
    ),

    skill_id: Optional[UUID] = Query(
        default=None
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return browse_opportunities(
        db=db,

        current_user=(
            current_user
        ),

        search=search,

        location=location,

        work_mode=work_mode,

        opportunity_type=(
            opportunity_type
        ),

        skill_id=skill_id,
    )




@router.get(
    "/me",
    response_model=List[
        OpportunityResponse
    ],
)
def my_opportunities(
    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_my_opportunities(
        db,
        current_user,
    )




@router.post(
    "",
    response_model=(
        OpportunityResponse
    ),
    status_code=201,
)
def create_opportunity_route(
    request: OpportunityCreateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return create_new_opportunity(
        db,
        current_user,
        request,
    )




@router.get(
    "/{opportunity_id}",
    response_model=(
        OpportunityResponse
    ),
)
def opportunity_detail(
    opportunity_id: UUID,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return get_opportunity_detail(
        db,
        current_user,
        opportunity_id,
    )




@router.put(
    "/{opportunity_id}",
    response_model=(
        OpportunityResponse
    ),
)
def update_opportunity_route(
    opportunity_id: UUID,

    request: OpportunityUpdateRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return update_existing_opportunity(
        db,
        current_user,
        opportunity_id,
        request,
    )




@router.patch(
    "/{opportunity_id}/status",
    response_model=(
        OpportunityResponse
    ),
)
def update_opportunity_status(
    opportunity_id: UUID,

    request: OpportunityStatusRequest,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    ),
):

    return change_opportunity_status(
        db,
        current_user,
        opportunity_id,
        request,
    )