from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session


from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.external_job import (
    ExternalJob,
)

from app.models.job_source import (
    JobSource,
)

from app.models.user import (
    User,
    UserRole,
)



from app.services.job_ingestion.excel_importer import (
    import_job_sources_excel,
)

from app.services.job_ingestion.ingestion_service import (
    JobIngestionService,
)


router = APIRouter(

    prefix="/admin/job-ingestion",

    tags=[
        "Admin Job Ingestion"
    ],
)


# ==================================================
# ADMIN AUTHORIZATION
# ==================================================

def require_admin(

    current_user: User = Depends(
        get_current_user
    ),

) -> User:

    if (
        current_user.role
        != UserRole.ADMIN
    ):

        raise HTTPException(

            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "Admin access required",
        )


    return current_user


# ==================================================
# IMPORT JOB SOURCES FROM EXCEL
# ==================================================

@router.post(
    "/sources/import"
)
async def import_sources(

    file: UploadFile =
        File(...),

    db: Session =
        Depends(get_db),

    _: User =
        Depends(require_admin),

):

    filename = (
        file.filename
        or ""
    ).lower()


    if not filename.endswith(
        ".xlsx"
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "Only .xlsx files "
                "are supported"
            ),
        )


    content = (
        await file.read()
    )


    try:

        return (
            import_job_sources_excel(
                db,
                content,
            )
        )


    except ValueError as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc),
        )


# ==================================================
# LIST JOB SOURCES
# ==================================================

@router.get(
    "/sources"
)
def list_sources(

    db: Session =
        Depends(get_db),

    _: User =
        Depends(require_admin),

):

    sources = (

        db.query(
            JobSource
        )

        .order_by(
            JobSource.company_name
        )

        .all()
    )


    results = []


    for source in sources:

        # NEW
        #
        # Count how many jobs currently exist
        # for this company/source.

        synced_job_count = (

            db.query(
                ExternalJob
            )

            .filter(
                ExternalJob.source_id
                == source.id
            )

            .count()
        )


        results.append({

            "id":
                source.id,

            "company_name":
                source.company_name,

            "careers_url":
                source.careers_url,

            "connector_type":
                source.connector_type,

            "connector_key":
                source.connector_key,

            "config_json":
                source.config_json,

            "is_active":
                source.is_active,

            "last_synced_at":
                source.last_synced_at,

            "last_sync_status":
                source.last_sync_status,

            "last_sync_error":
                source.last_sync_error,

            # NEW
            "synced_job_count":
                synced_job_count,

        })


    return results


# ==================================================
# SYNC ALL ACTIVE SOURCES
# ==================================================

@router.post(
    "/sync"
)
async def sync_all_sources(

    db: Session =
        Depends(get_db),

    _: User =
        Depends(require_admin),

):

    service = (
        JobIngestionService(
            db
        )
    )


    results = (
        await service.sync_all()
    )


    return {
        "results":
            results,
    }


# ==================================================
# SYNC ONE SOURCE
# ==================================================

@router.post(
    "/sources/{source_id}/sync"
)
async def sync_one_source(

    source_id: int,

    db: Session =
        Depends(get_db),

    _: User =
        Depends(require_admin),

):

    source = (

        db.query(
            JobSource
        )

        .filter(
            JobSource.id
            == source_id
        )

        .first()
    )


    if not source:

        raise HTTPException(

            status_code=404,

            detail=(
                "Job source not found"
            ),
        )


    if not source.is_active:

        raise HTTPException(

            status_code=400,

            detail=(
                "Job source is disabled."
            ),
        )


    service = (
        JobIngestionService(
            db
        )
    )


    return (
        await service.sync_source(
            source
        )
    )


# ==================================================
# NEW
# DELETE ALL JOBS FOR ONE SOURCE
# ==================================================

@router.delete(
    "/sources/{source_id}/jobs"
)
def delete_synced_jobs(

    source_id: int,

    db: Session =
        Depends(get_db),

    _: User =
        Depends(require_admin),

):

    source = (

        db.query(
            JobSource
        )

        .filter(
            JobSource.id
            == source_id
        )

        .first()
    )


    if not source:

        raise HTTPException(

            status_code=404,

            detail=(
                "Job source not found"
            ),
        )


    service = (
        JobIngestionService(
            db
        )
    )


    try:

        return (
            service.delete_source_jobs(
                source
            )
        )


    except RuntimeError as exc:

        raise HTTPException(

            status_code=500,

            detail=str(exc),
        )