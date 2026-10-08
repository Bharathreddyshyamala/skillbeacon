from abc import ABC, abstractmethod

from app.models.job_source import JobSource
from app.services.job_ingestion.types import (
    ConnectorFetchResult,
)


class BaseJobConnector(ABC):

    def __init__(
        self,
        source: JobSource,
    ):
        self.source = source
        self.config = (
            source.config_json or {}
        )

    @abstractmethod
    async def fetch_jobs(
        self,
    ) -> ConnectorFetchResult:
        pass