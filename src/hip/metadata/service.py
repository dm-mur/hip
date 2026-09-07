"""Metadata service contracts."""

from typing import Protocol

from hip.metadata.dhis2 import DHIS2Metadata


class DHIS2MetadataService(Protocol):
    """Resolve human-readable metadata for DHIS2 identifiers."""

    def preload(
        self,
        *,
        data_elements: set[str],
        org_units: set[str],
        category_option_combos: set[str],
    ) -> None:
        ...

    def resolve(
        self,
        *,
        data_element: str,
        org_unit: str,
        category_option_combo: str | None,
        attribute_option_combo: str | None,
    ) -> DHIS2Metadata:
        ...
        """Return metadata associated with one DHIS2 data value."""
