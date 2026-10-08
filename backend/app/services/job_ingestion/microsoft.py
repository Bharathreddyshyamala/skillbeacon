import asyncio
from typing import Any, Optional

import httpx

from app.services.job_ingestion.base import (
    BaseJobConnector,
)
from app.services.job_ingestion.types import (
    ConnectorFetchResult,
    NormalizedJob,
)
from app.services.job_ingestion.utils import (
    clean_html,
    parse_datetime,
    request_json,
    stringify_location,
)


class MicrosoftConnector(
    BaseJobConnector
):

    BASE_URL = (
        "https://apply.careers."
        "microsoft.com"
    )

    DOMAIN = "microsoft.com"

    def _pick(
        self,
        data: dict,
        *names: str,
    ) -> Any:

        for name in names:
            value = data.get(name)

            if value not in (
                None,
                "",
                [],
                {},
            ):
                return value

        return None

    def _extract_id(
        self,
        raw: dict,
    ) -> Optional[str]:

        value = self._pick(
            raw,
            "id",
            "position_id",
            "positionId",
            "job_id",
        )

        if value is None:
            return None

        return str(value)

    async def _get_detail(
        self,
        client: httpx.AsyncClient,
        job_id: str,
        semaphore: asyncio.Semaphore,
    ) -> dict:

        async with semaphore:

            url = (
                f"{self.BASE_URL}"
                f"/api/apply/v2/jobs/"
                f"{job_id}"
            )

            try:
                return await request_json(
                    client,
                    url,
                    params={
                        "domain": self.DOMAIN,
                        "hl": "en",
                    },
                )

            except RuntimeError:
                # If detail API changes,
                # caller can still use summary.
                return {}

    async def fetch_jobs(
        self,
    ) -> ConnectorFetchResult:

        max_jobs = int(
            self.config.get(
                "max_jobs",
                1000,
            )
        )

        max_pages = int(
            self.config.get(
                "max_pages",
                200,
            )
        )

        concurrency = min(
            int(
                self.config.get(
                    "detail_concurrency",
                    3,
                )
            ),
            3,
        )

        domain = (
            self.source.connector_key
            or self.DOMAIN
        )

        if domain != "microsoft.com":
            raise ValueError(
                "Microsoft connector requires "
                "connector_key=microsoft.com"
            )

        headers = {
            "Accept": "application/json",
            "Content-Type": (
                "application/json"
            ),
            "User-Agent": (
                "Mozilla/5.0 "
                "SkillBeaconJobIndexer/1.0"
            ),
        }

        normalized_jobs = []

        start = 0
        seen_ids = set()
        total_jobs = None

        semaphore = asyncio.Semaphore(
            concurrency
        )

        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        ) as client:

            for _ in range(max_pages):

                search_url = (
                    f"{self.BASE_URL}"
                    "/api/apply/v2/jobs"
                )

                data = await request_json(
                    client,
                    search_url,
                    params={
                        "domain": domain,
                        "hl": "en",
                        "start": start,
                        "sort_by": "timestamp",
                    },
                )

                positions = (
                    data.get("positions")
                    or []
                )

                if total_jobs is None:
                    total_jobs = (
                        data.get("totalJobs")
                    )

                if not positions:
                    break

                page_jobs = []

                for raw in positions:

                    job_id = (
                        self._extract_id(
                            raw
                        )
                    )

                    if not job_id:
                        continue

                    # Prevent infinite pagination
                    # if upstream returns same page.
                    if job_id in seen_ids:
                        continue

                    seen_ids.add(job_id)

                    page_jobs.append(
                        (
                            job_id,
                            raw,
                        )
                    )

                if not page_jobs:
                    break

                detail_results = (
                    await asyncio.gather(
                        *[
                            self._get_detail(
                                client,
                                job_id,
                                semaphore,
                            )
                            for (
                                job_id,
                                _
                            ) in page_jobs
                        ]
                    )
                )

                for (
                    (job_id, summary),
                    detail,
                ) in zip(
                    page_jobs,
                    detail_results,
                ):

                    raw = {
                        **summary,
                        **detail,
                    }

                    title = self._pick(
                        raw,
                        "name",
                        "title",
                        "job_title",
                        "position_name",
                    )

                    location = (
                        stringify_location(
                            self._pick(
                                raw,
                                "locations",
                                "location",
                                "ats_location",
                            )
                        )
                    )

                    description = clean_html(
                        self._pick(
                            raw,
                            "job_description",
                            "description",
                            "descriptionHtml",
                        )
                    )

                    job_url = self._pick(
                        raw,
                        "canonicalPositionUrl",
                        "canonical_position_url",
                        "url",
                    )

                    if not job_url:
                        job_url = (
                            f"{self.BASE_URL}"
                            f"/careers/job/"
                            f"{job_id}"
                            f"?domain={domain}"
                        )

                    apply_url = self._pick(
                        raw,
                        "applyUrl",
                        "apply_url",
                        "application_url",
                    )

                    normalized_jobs.append(
                        NormalizedJob(
                            external_job_id=(
                                job_id
                            ),
                            company_name=(
                                self.source
                                .company_name
                            ),
                            title=(
                                str(title)
                                if title
                                else "Untitled Job"
                            ),
                            description=(
                                description
                            ),
                            location=(
                                location
                            ),
                            employment_type=(
                                self._pick(
                                    raw,
                                    "employment_type",
                                    "employmentType",
                                    "type",
                                )
                            ),
                            workplace_type=(
                                self._pick(
                                    raw,
                                    "work_location_option",
                                    "workSite",
                                    "work_site",
                                )
                            ),
                            department=(
                                self._pick(
                                    raw,
                                    "department",
                                    "profession",
                                    "job_function",
                                )
                            ),
                            job_url=job_url,
                            apply_url=(
                                apply_url
                                or job_url
                            ),
                            posted_at=(
                                parse_datetime(
                                    self._pick(
                                        raw,
                                        "posted_timestamp",
                                        "externally_posted_ts",
                                        "postedDate",
                                    )
                                )
                            ),
                            raw_payload=raw,
                        )
                    )

                    if (
                        len(normalized_jobs)
                        >= max_jobs
                    ):
                        return (
                            ConnectorFetchResult(
                                jobs=(
                                    normalized_jobs
                                ),
                                is_complete=False,
                            )
                        )

                # Eightfold normally pages by
                # number of returned records.
                start += len(positions)

                if (
                    total_jobs
                    and start
                    >= int(total_jobs)
                ):
                    break

        is_complete = True

        if (
            total_jobs is not None
            and len(normalized_jobs)
            < int(total_jobs)
        ):
            is_complete = False

        return ConnectorFetchResult(
            jobs=normalized_jobs,
            is_complete=is_complete,
        )