"""In-memory DHIS2 metadata resolver."""

from hip.metadata.dhis2 import DHIS2Metadata


class InMemoryDHIS2MetadataService:
    """Resolve DHIS2 metadata from in-memory lookup dictionaries."""

    def __init__(
        self,
        *,
        data_elements: dict[str, str] | None = None,
        org_units: dict[str, str] | None = None,
        category_option_combos: dict[str, str] | None = None,
        attribute_option_combos: dict[str, str] | None = None,
    ) -> None:
        self.data_elements = data_elements or {}
        self.org_units = org_units or {}
        self.category_option_combos = category_option_combos or {}
        self.attribute_option_combos = attribute_option_combos or {}

    def resolve(
        self,
        *,
        data_element: str,
        org_unit: str,
        category_option_combo: str | None,
        attribute_option_combo: str | None,
    ) -> DHIS2Metadata:
        """Resolve metadata for one DHIS2 data value."""

        return DHIS2Metadata(
            data_element_name=self.data_elements.get(data_element),
            org_unit_name=self.org_units.get(org_unit),
            category_option_combo_name=(
                self.category_option_combos.get(category_option_combo)
                if category_option_combo is not None
                else None
            ),
            attribute_option_combo_name=(
                self.attribute_option_combos.get(attribute_option_combo)
                if attribute_option_combo is not None
                else None
            ),
        )

    def preload(
        self,
        *,
        data_elements: set[str],
        org_units: set[str],
        category_option_combos: set[str],
    ) -> None:
        """Metadata is already available in memory."""