"""
Canonical DHIS2 record model.

This model represents the common structure HIP uses internally,
regardless of how individual DHIS2 instances name or structure
their source fields.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DHIS2Record:
    """Canonical representation of a DHIS2 data record."""

    batch_id: str
    source_instance: str

    dataset_id: str | None
    data_element: str | None
    data_element_name: str | None

    org_unit: str | None
    org_unit_name: str | None

    period: str | None

    category_option_combo: str | None
    category_option_combo_name: str | None

    attribute_option_combo: str | None
    attribute_option_combo_name: str | None

    value: str | None

    comment: str | None
    followup: str | None
    stored_by: str | None

    created_at_source: Any | None
    last_updated_at_source: Any | None

    raw_payload: dict[str, Any]

    record_hash: str
