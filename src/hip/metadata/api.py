"""DHIS2 API-backed metadata service."""

from typing import Any

import requests

from hip.config.settings import DHIS2Settings
from hip.metadata.dhis2 import DHIS2Metadata


class DHIS2APIMetadataService:
    """Resolve metadata from one specific DHIS2 instance."""

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

        self.data_elements: dict[str, str] = {}
        self.org_units: dict[str, str] = {}
        self.category_option_combos: dict[str, str] = {}

    def _url(
        self,
        endpoint: str,
    ) -> str:
        """Build an absolute DHIS2 API URL."""

        return (
            f"{self.settings.base_url.rstrip('/')}/"
            f"{endpoint.lstrip('/')}"
        )

    def _fetch_lookup(
        self,
        endpoint: str,
        collection_key: str,
        ids: set[str],
    ) -> dict[str, str]:
        if not ids:
            return {}

        filter_value = ",".join(sorted(ids))

        response = requests.get(
            self._url(endpoint),
            params={
                "fields": "id,name",
                "filter": f"id:in:[{filter_value}]",
                "paging": "false",
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
            item["id"]: item["name"]
            for item in payload.get(collection_key, [])
            if item.get("id") and item.get("name")
        }

    def preload(
        self,
        *,
        data_elements: set[str],
        org_units: set[str],
        category_option_combos: set[str],
    ) -> None:
        self.data_elements.update(
            self._fetch_lookup(
                endpoint="/api/dataElements",
                collection_key="dataElements",
                ids=data_elements,
            )
        )

        self.org_units.update(
            self._fetch_lookup(
                endpoint="/api/organisationUnits",
                collection_key="organisationUnits",
                ids=org_units,
            )
        )

        self.category_option_combos.update(
            self._fetch_lookup(
                endpoint="/api/categoryOptionCombos",
                collection_key="categoryOptionCombos",
                ids=category_option_combos,
            )
        )

    def resolve(
        self,
        *,
        data_element: str,
        org_unit: str,
        category_option_combo: str | None,
        attribute_option_combo: str | None,
    ) -> DHIS2Metadata:
        """Resolve names from the currently loaded metadata cache."""

        return DHIS2Metadata(
            data_element_name=self.data_elements.get(data_element),
            org_unit_name=self.org_units.get(org_unit),
            category_option_combo_name=(
                self.category_option_combos.get(
                    category_option_combo
                )
                if category_option_combo is not None
                else None
            ),
            attribute_option_combo_name=(
                self.category_option_combos.get(
                    attribute_option_combo
                )
                if attribute_option_combo is not None
                else None
            ),
        )
