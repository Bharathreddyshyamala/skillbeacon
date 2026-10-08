from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.external_job import ExternalJob
from app.models.job_source import JobSource

from app.services.job_ingestion.factory import (
    get_connector,
)


class JobIngestionService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    async def sync_source(
        self,
        source: JobSource,
    ) -> dict:

        connector = get_connector(
            source
        )

        now = datetime.now(
            timezone.utc
        )

        try:

            result = (
                await connector.fetch_jobs()
            )

            seen_external_ids = set()

            created = 0
            updated = 0


            for item in result.jobs:

                external_id = str(
                    item.external_job_id
                )

                seen_external_ids.add(
                    external_id
                )


                existing = (
                    self.db.query(
                        ExternalJob
                    )
                    .filter(
                        ExternalJob.source_id
                        == source.id,

                        ExternalJob.external_job_id
                        == external_id,
                    )
                    .first()
                )


                values = {

                    "company_name":
                        item.company_name,

                    "title":
                        item.title,

                    "description":
                        item.description,

                    "location":
                        item.location,

                    "city":
                        item.city,

                    "state":
                        item.state,

                    "country":
                        item.country,

                    "employment_type":
                        item.employment_type,

                    "workplace_type":
                        item.workplace_type,

                    "department":
                        item.department,

                    "job_url":
                        item.job_url,

                    "apply_url":
                        item.apply_url,

                    "posted_at":
                        item.posted_at,

                    "source_updated_at":
                        item.source_updated_at,

                    "source_rank":
                        item.source_rank,

                    "raw_payload":
                        item.raw_payload,

                    "last_seen_at":
                        now,

                    "is_active":
                        True,
                }


                if existing:

                    for key, value in values.items():

                        setattr(
                            existing,
                            key,
                            value,
                        )

                    updated += 1


                else:

                    new_job = ExternalJob(

                        source_id=
                            source.id,

                        external_job_id=
                            external_id,

                        first_seen_at=
                            now,

                        **values,
                    )

                    self.db.add(
                        new_job
                    )

                    created += 1


            deactivated = 0


            # Deactivate jobs that disappeared when the
            # connector fetched the complete source or
            # an authoritative recent-results window.
            #
            # Example:
            # Amazon has 5000 jobs but max_jobs=100.
            # A normal partial fetch retains the other
            # 4900. A recent-only window intentionally
            # hides jobs outside its configured limit.

            if (
                result.is_complete
                or result.deactivate_unseen
            ):

                active_jobs = (
                    self.db.query(
                        ExternalJob
                    )
                    .filter(
                        ExternalJob.source_id
                        == source.id,

                        ExternalJob.is_active
                        .is_(True),
                    )
                    .all()
                )


                for existing in active_jobs:

                    if (
                        existing.external_job_id
                        not in seen_external_ids
                    ):

                        existing.is_active = (
                            False
                        )

                        deactivated += 1


            source.last_synced_at = now

            source.last_sync_status = (
                "success"
            )

            source.last_sync_error = None


            self.db.commit()


            return {

                "source_id":
                    source.id,

                "company":
                    source.company_name,

                "connector":
                    source.connector_type,

                "fetched":
                    len(result.jobs),

                "created":
                    created,

                "updated":
                    updated,

                "deactivated":
                    deactivated,

                "complete":
                    result.is_complete,

                "status":
                    "success",
            }


        except Exception as exc:

            self.db.rollback()


            # Reload source after rollback so we can
            # safely store the failure information.

            source = (
                self.db.query(
                    JobSource
                )
                .filter(
                    JobSource.id
                    == source.id
                )
                .first()
            )


            if source:

                source.last_synced_at = now

                source.last_sync_status = (
                    "failed"
                )

                source.last_sync_error = (
                    str(exc)[:5000]
                )

                self.db.commit()


            return {

                "source_id":
                    source.id
                    if source
                    else None,

                "company":
                    source.company_name
                    if source
                    else None,

                "status":
                    "failed",

                "error":
                    str(exc),
            }


    async def sync_all(
        self,
    ) -> list:

        sources = (
            self.db.query(
                JobSource
            )
            .filter(
                JobSource.is_active
                .is_(True)
            )
            .all()
        )


        results = []


        # Sync sequentially.
        #
        # This avoids sending many simultaneous
        # requests to Amazon/Microsoft/etc.

        for source in sources:

            result = (
                await self.sync_source(
                    source
                )
            )

            results.append(
                result
            )


        return results


    # ==================================================
    # NEW
    # Delete all jobs belonging to one configured source
    # ==================================================

    def delete_source_jobs(
        self,
        source: JobSource,
    ) -> dict:
        """
        Permanently remove all ExternalJob records
        synchronized from this source.

        The JobSource itself is NOT deleted.

        Example:

        Amazon JobSource remains configured,
        but all previously imported Amazon jobs
        are removed from external_jobs.
        """

        try:

            deleted_count = (

                self.db.query(
                    ExternalJob
                )
                .filter(
                    ExternalJob.source_id
                    == source.id
                )
                .delete(
                    synchronize_session=False
                )

            )


            # We intentionally keep:
            #
            # source.is_active
            # source.careers_url
            # source.connector_type
            # source.connector_key
            #
            # because the source can be synced again.

            source.last_sync_status = (
                "cleared"
            )

            source.last_sync_error = None


            self.db.commit()


            return {

                "source_id":
                    source.id,

                "company":
                    source.company_name,

                "connector":
                    source.connector_type,

                "deleted":
                    deleted_count,

                "status":
                    "success",

                "message":
                    (
                        f"Deleted "
                        f"{deleted_count} "
                        f"synced jobs for "
                        f"{source.company_name}."
                    ),
            }


        except Exception as exc:

            self.db.rollback()

            raise RuntimeError(
                (
                    "Unable to delete synced "
                    f"jobs for "
                    f"{source.company_name}: "
                    f"{exc}"
                )
            )
