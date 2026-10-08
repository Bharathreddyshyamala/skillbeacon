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
    parse_datetime,
    request_json,
)


class GreenhouseConnector(
    BaseJobConnector
):

    BASE_URL = (
        "https://boards-api."
        "greenhouse.io/v1/boards"
    )

    async def fetch_jobs(
        self,
    ) -> ConnectorFetchResult:

        board_token = (
            self.source.connector_key
            or ""
        ).strip()

        if not re.fullmatch(
            r"[A-Za-z0-9_-]+",
            board_token,
        ):
            raise ValueError(
                "Invalid Greenhouse board token"
            )

        url = (
            f"{self.BASE_URL}/"
            f"{board_token}/jobs"
        )

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

            data = await request_json(
                client,
                url,
                params={
                    "content": "true"
                },
            )

        normalized_jobs = []

        for raw in data.get(
            "jobs",
            [],
        ):
            external_id = raw.get("id")

            if external_id is None:
                continue

            location = (
                raw.get("location")
                or {}
            ).get("name")

            job_url = raw.get(
                "absolute_url"
            )

            if not job_url:
                continue

            normalized_jobs.append(
                NormalizedJob(
                    external_job_id=str(
                        external_id
                    ),
                    company_name=(
                        self.source.company_name
                    ),
                    title=(
                        raw.get("title")
                        or "Untitled Job"
                    ),
                    description=clean_html(
                        raw.get("content")
                    ),
                    location=location,
                    job_url=job_url,
                    apply_url=job_url,
                    source_updated_at=(
                        parse_datetime(
                            raw.get(
                                "updated_at"
                            )
                        )
                    ),
                    raw_payload=raw,
                )
            )

        return ConnectorFetchResult(
            jobs=normalized_jobs,
            is_complete=True,
        )