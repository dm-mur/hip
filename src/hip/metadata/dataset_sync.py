"""Synchronization of DHIS2 dataset metadata."""

from typing import Any

from hip.metadata.dataset_api import DHIS2DatasetMetadataService
from hip.repositories.dataset import DHIS2DatasetRepository


class DHIS2DatasetMetadataSync:
    """Fetch and persist authoritative DHIS2 dataset metadata."""

    def __init__(
        self,
        *,
        api_service: DHIS2DatasetMetadataService,
        repository: DHIS2DatasetRepository,
    ) -> None:
        self.api_service = api_service
        self.repository = repository

    def sync(
        self,
        *,
        source_instance: str,
        dataset_id: str,
    ) -> dict[str, Any]:
        """Fetch and persist metadata for one DHIS2 dataset."""

        metadata = self.api_service.fetch(dataset_id)

        self.repository.upsert(
            source_instance=source_instance,
            dataset_id=metadata["dataset_id"],
            dataset_name=metadata["dataset_name"],
            period_type=metadata["period_type"],
        )

        return metadata
