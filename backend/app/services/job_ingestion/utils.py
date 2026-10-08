import asyncio
from datetime import datetime
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


def clean_html(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    soup = BeautifulSoup(
        value,
        "html.parser",
    )

    text = soup.get_text(
        separator="\n",
        strip=True,
    )

    return text or None


def parse_datetime(
    value: Any,
) -> Optional[datetime]:

    if value is None:
        return None

    try:
        # Unix milliseconds
        if isinstance(value, (int, float)):
            number = float(value)

            if number > 10_000_000_000:
                number = number / 1000

            return datetime.fromtimestamp(
                number
            ).astimezone()

        value = str(value).strip()

        if not value:
            return None

        return date_parser.parse(value)

    except (ValueError, TypeError, OverflowError):
        return None


async def request_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: Optional[dict] = None,
    retries: int = 3,
) -> Any:

    last_error = None

    for attempt in range(retries):
        try:
            response = await client.get(
                url,
                params=params,
            )

            if response.status_code == 429:
                await asyncio.sleep(
                    2 ** attempt
                )
                continue

            if response.status_code >= 500:
                await asyncio.sleep(
                    2 ** attempt
                )
                continue

            response.raise_for_status()

            return response.json()

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.HTTPStatusError,
        ) as exc:

            last_error = exc

            if attempt < retries - 1:
                await asyncio.sleep(
                    2 ** attempt
                )

    raise RuntimeError(
        f"External job request failed: "
        f"{url}: {last_error}"
    )


def stringify_location(
    value: Any,
) -> Optional[str]:

    if value is None:
        return None

    if isinstance(value, str):
        return value.strip() or None

    if isinstance(value, list):
        values = [
            stringify_location(item)
            for item in value
        ]

        return " | ".join(
            value
            for value in values
            if value
        ) or None

    if isinstance(value, dict):
        for key in (
            "name",
            "location",
            "display_name",
            "city",
        ):
            if value.get(key):
                return str(value[key])

        return ", ".join(
            str(item)
            for item in value.values()
            if item
        ) or None

    return str(value)