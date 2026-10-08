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


class AmazonConnector(BaseJobConnector):

    SEARCH_URL = (
        "https://www.amazon.jobs"
        "/en/search.json"
    )

    BASE_URL = "https://www.amazon.jobs"

    async def fetch_jobs(
        self,
    ) -> ConnectorFetchResult:

        page_size = min(
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
                2000,
            )
        )

        country = self.config.get(
            "country"
        )

        query = self.config.get(
            "base_query",
            "",
        )

        location = self.config.get(
            "location",
            "",
        )
        sort = str(
            self.config.get(
                "sort",
                "recent",
            )
        ).strip().lower()

        if sort not in {
            "recent",
            "relevant",
            "distance",
        }:
            raise ValueError(
                "Invalid Amazon sort value: "
                f"{sort}"
            )

        normalized_jobs = []

        offset = 0
        total_hits = None

        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 "
                "SkillBeaconJobIndexer/1.0"
            ),
        }

        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        ) as client:

            while True:

                params = {
                    "base_query": query,
                    "loc_query": location,
                    "offset": offset,
                    "result_limit": page_size,
                    "sort": sort,
                }

                if country:
                    params["country"] = country

                data = await request_json(
                    client,
                    self.SEARCH_URL,
                    params=params,
                )

                if data.get("error"):
                    raise RuntimeError(
                        f"Amazon API error: "
                        f"{data['error']}"
                    )

                if total_hits is None:
                    total_hits = int(
                        data.get("hits", 0)
                    )

                raw_jobs = (
                    data.get("jobs")
                    or []
                )

                if not raw_jobs:
                    break

                for page_index, raw in enumerate(
                    raw_jobs
                ):

                    source_rank = (
                        offset + page_index
                    )

                    external_id = (
                        raw.get("id_icims")
                        or raw.get("id")
                    )

                    if not external_id:
                        continue

                    job_path = (
                        raw.get("job_path")
                        or ""
                    )

                    if job_path.startswith(
                        "http"
                    ):
                        job_url = job_path
                    else:
                        job_url = (
                            self.BASE_URL
                            + job_path
                        )

                    description_parts = []

                    description = clean_html(
                        raw.get(
                            "description"
                        )
                    )

                    if description:
                        description_parts.append(
                            description
                        )

                    basic = clean_html(
                        raw.get(
                            "basic_qualifications"
                        )
                    )

                    if basic:
                        description_parts.append(
                            "Basic Qualifications\n"
                            + basic
                        )

                    preferred = clean_html(
                        raw.get(
                            "preferred_qualifications"
                        )
                    )

                    if preferred:
                        description_parts.append(
                            "Preferred Qualifications\n"
                            + preferred
                        )

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
                            description=(
                                "\n\n".join(
                                    description_parts
                                )
                                or None
                            ),
                            location=raw.get(
                                "location"
                            ),
                            city=raw.get(
                                "city"
                            ),
                            country=raw.get(
                                "country_code"
                            ),
                            employment_type=raw.get(
                                "job_schedule_type"
                            ),
                            department=(
                                raw.get(
                                    "job_category"
                                )
                                or raw.get(
                                    "business_category"
                                )
                            ),
                            job_url=job_url,
                            apply_url=(
                                raw.get(
                                    "url_next_step"
                                )
                                or job_url
                            ),
                            posted_at=parse_datetime(
                                raw.get(
                                    "posted_date"
                                )
                            ),
                            source_rank=source_rank,
                            raw_payload=raw,
                        )
                    )

                    if (
                        len(normalized_jobs)
                        >= max_jobs
                    ):
                        return ConnectorFetchResult(
                            jobs=normalized_jobs,
                            is_complete=(
                                total_hits is not None
                                and len(
                                    normalized_jobs
                                )
                                >= total_hits
                            ),
                            deactivate_unseen=(
                                sort == "recent"
                            ),
                        )

                offset += len(raw_jobs)

                if (
                    total_hits is not None
                    and offset >= total_hits
                ):
                    break

                if len(raw_jobs) < page_size:
                    break

        return ConnectorFetchResult(
            jobs=normalized_jobs,
            is_complete=True,
            deactivate_unseen=(
                sort == "recent"
            ),
        )
