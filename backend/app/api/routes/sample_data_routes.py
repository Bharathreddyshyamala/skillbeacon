from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.models.user import User

from app.schemas.sample_data_schema import (
    SampleDataBatchListResponse,
    SampleDataDeleteResponse,
    SampleDataImportResponse,
    SampleDataPreviewResponse,
)

from app.services.sample_data_service import (
    get_sample_data_batches,
    import_sample_data,
    preview_sample_data,
    remove_sample_data_batch,
)


from app.api.dependencies import get_current_user
from app.core.database import get_db


router = APIRouter(
    prefix="/admin/sample-data",
    tags=["Admin Sample Data"],
)


@router.post(
    "/preview",
    response_model=(
        SampleDataPreviewResponse
    ),
)
async def preview_route(
    file: UploadFile = File(...),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return await (
        preview_sample_data(
            db=db,
            current_user=current_user,
            upload=file,
        )
    )


@router.post(
    "/import",
    response_model=(
        SampleDataImportResponse
    ),
)
async def import_route(
    file: UploadFile = File(...),
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return await (
        import_sample_data(
            db=db,
            current_user=current_user,
            upload=file,
        )
    )


@router.get(
    "/batches",
    response_model=(
        SampleDataBatchListResponse
    ),
)
def batches_route(
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return get_sample_data_batches(
        db=db,
        current_user=current_user,
    )


@router.delete(
    "/batches/{batch_id}",
    response_model=(
        SampleDataDeleteResponse
    ),
)
def delete_batch_route(
    batch_id: UUID,
    db: Session = Depends(
        get_db
    ),
    current_user: User = Depends(
        get_current_user
    ),
):

    return remove_sample_data_batch(
        db=db,
        current_user=current_user,
        batch_id=batch_id,
    )