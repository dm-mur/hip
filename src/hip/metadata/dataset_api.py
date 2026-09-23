"""DHIS2 API service for dataset metadata."""

from typing import Any

import requests

from hip.config.settings import DHIS2Settings


class DHIS2DatasetMetadataService:
    """Retrieve dataset metadata from one specific DHIS2 instance."""

    def __init__(
        self,
        *,
        source_instance: str,
        settings: DHIS2Settings,
    ) -> None:
        if not source_instance.strip():
            raise ValueError("source_instance is required")

        self.source_instance = source_instance
        self.settings = settings

    def _url(self, dataset_id: str) -> str:
        """Build the DHIS2 dataset metadata URL."""

        return (
            f"{self.settings.base_url.rstrip('/')}/"
            f"api/dataSets/{dataset_id}"
        )

    def fetch(
        self,
        dataset_id: str,
    ) -> dict[str, Any]:
        """Retrieve metadata for one DHIS2 dataset."""

        response = requests.get(
            self._url(dataset_id),
            params={
                "fields": "id,name,periodType",
            },
            auth=(
                self.settings.username,
                self.settings.password,
            ),
            timeout=60,
        )

        response.raise_for_status()

        payload: dict[str, Any] = response.json()

        return {
            "dataset_id": payload["id"],
            "dataset_name": payload["name"],
            "period_type": payload["periodType"],
        }
