import re

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
    request_json,
)


class LeverConnector(
    BaseJobConnector
):

    async def fetch_jobs(
        self,
    ) -> ConnectorFetchResult:

        site = (
            self.source.connector_key
            or ""
        ).strip()

        if not re.fullmatch(
            r"[A-Za-z0-9_-]+",
            site,
        ):
            raise ValueError(
                "Invalid Lever site slug"
            )

        region = str(
            self.config.get(
                "region",
                "global",
            )
        ).lower()

        if region == "eu":
            base_url = (
                "https://api.eu."
                "lever.co/v0/postings"
            )
        else:
            base_url = (
                "https://api.lever.co"
                "/v0/postings"
            )

        url = (
            f"{base_url}/{site}"
        )

        limit = min(
            int(
                self.config.get(
                    "page_size",
                    100,
                )
            ),
            100,
        )

        max_jobs = int(
            self.config.get(
                "max_jobs",
                5000,
            )
        )

        skip = 0
        normalized_jobs = []

        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "SkillBeaconJobIndexer/1.0"
            ),
        }

        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
        ) as client:

            while True:

                raw_jobs = await request_json(
                    client,
                    url,
                    params={
                        "mode": "json",
                        "skip": skip,
                        "limit": limit,
                    },
                )

                if not raw_jobs:
                    break

                for raw in raw_jobs:

                    external_id = raw.get(
                        "id"
                    )

                    if not external_id:
                        continue

                    categories = (
                        raw.get(
                            "categories"
                        )
                        or {}
                    )

                    job_url = (
                        raw.get(
                            "hostedUrl"
                        )
                        or raw.get(
                            "applyUrl"
                        )
                    )

                    if not job_url:
                        continue

                    description = (
                        raw.get(
                            "descriptionPlain"
                        )
                        or clean_html(
                            raw.get(
                                "description"
                            )
                        )
                    )

                    normalized_jobs.append(
                        NormalizedJob(
                            external_job_id=(
                                str(
                                    external_id
                                )
                            ),
                            company_name=(
                                self.source
                                .company_name
                            ),
                            title=(
                                raw.get("text")
                                or "Untitled Job"
                            ),
                            description=(
                                description
                            ),
                            location=(
                                categories.get(
                                    "location"
                                )
                            ),
                            country=raw.get(
                                "country"
                            ),
                            employment_type=(
                                categories.get(
                                    "commitment"
                                )
                            ),
                            workplace_type=(
                                raw.get(
                                    "workplaceType"
                                )
                            ),
                            department=(
                                categories.get(
                                    "department"
                                )
                                or categories.get(
                                    "team"
                                )
                            ),
                            job_url=job_url,
                            apply_url=(
                                raw.get(
                                    "applyUrl"
                                )
                                or job_url
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

                skip += len(raw_jobs)

                if len(raw_jobs) < limit:
                    break

        return ConnectorFetchResult(
            jobs=normalized_jobs,
            is_complete=True,
        )