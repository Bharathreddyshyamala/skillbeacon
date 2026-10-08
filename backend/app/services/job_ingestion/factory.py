from app.models.job_source import JobSource

from app.services.job_ingestion.base import (
    BaseJobConnector,
)
from app.services.job_ingestion.amazon import (
    AmazonConnector,
)
from app.services.job_ingestion.microsoft import (
    MicrosoftConnector,
)
from app.services.job_ingestion.greenhouse import (
    GreenhouseConnector,
)
from app.services.job_ingestion.lever import (
    LeverConnector,
)


def get_connector(
    source: JobSource,
) -> BaseJobConnector:

    connector_type = (
        source.connector_type
        .strip()
        .lower()
    )

    connectors = {
        "amazon": AmazonConnector,
        "microsoft": MicrosoftConnector,
        "greenhouse": GreenhouseConnector,
        "lever": LeverConnector,
    }

    connector_class = connectors.get(
        connector_type
    )

    if connector_class is None:
        raise ValueError(
            "Unsupported connector type: "
            f"{connector_type}"
        )

    return connector_class(source)