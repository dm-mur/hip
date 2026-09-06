"""DHIS2 metadata models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DHIS2Metadata:
    """Human-readable metadata associated with a DHIS2 data value."""

    data_element_name: str | None = None
    org_unit_name: str | None = None
    category_option_combo_name: str | None = None
    attribute_option_combo_name: str | None = None
